from __future__ import annotations

import json
import logging
from io import BytesIO
from pathlib import Path
from typing import Tuple

import numpy as np
from django.conf import settings
from PIL import Image

logger = logging.getLogger(__name__)

# Flags para ML
ML_ENABLED = getattr(settings, "PIXELCHECK_ML_ENABLED", True)
TORCH_AVAILABLE = False
torch = None
Resize = CenterCrop = Compose = Normalize = ToTensor = None

# Intentar cargar torch/torchvision solo si ML está habilitado
if ML_ENABLED:
    try:
        import torch as _torch
        from torchvision.transforms import CenterCrop as _CenterCrop
        from torchvision.transforms import Compose as _Compose
        from torchvision.transforms import Normalize as _Normalize
        from torchvision.transforms import Resize as _Resize
        from torchvision.transforms import ToTensor as _ToTensor

        torch = _torch
        Resize = _Resize
        CenterCrop = _CenterCrop
        Compose = _Compose
        Normalize = _Normalize
        ToTensor = _ToTensor
        TORCH_AVAILABLE = True
        logger.info("Torch/torchvision cargados correctamente.")
    except BaseException as exc:
        TORCH_AVAILABLE = False
        logger.error("No se pudo cargar torch/torchvision. ML desactivado. Error: %s", exc)
else:
    logger.info("PIXELCHECK_ML_ENABLED=False, se omite carga de torch/torchvision.")


class PixelCheckInference:
    """
    Carga el modelo entrenado (TorchScript) y expone un método predict.
    Si ML está deshabilitado o torch no está disponible, opera en modo dummy.
    """

    _instance: "PixelCheckInference | None" = None

    @classmethod
    def instance(cls) -> "PixelCheckInference":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.enabled = ML_ENABLED and TORCH_AVAILABLE
        if not self.enabled:
            self.metadata = {}
            self.ai_index = 0
            self.model = None
            self.device = None
            logger.warning("PixelCheckInference en modo dummy (ML deshabilitado o torch no disponible).")
            return

        model_path = Path(settings.PIXELCHECK_MODEL_PATH)
        if not model_path.exists():
            raise FileNotFoundError(f"No se encontró el modelo en {model_path}")

        metadata_path = model_path.parent / "metadata.json"
        self.metadata = json.loads(metadata_path.read_text()) if metadata_path.exists() else {}
        self.ai_index = int(self.metadata.get("ai_class_index", 0))

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = torch.jit.load(model_path, map_location=self.device).eval()

        self.transform = Compose(
            [
                Resize((256, 256)),
                CenterCrop(224),
                ToTensor(),
                Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
            ]
        )

    def predict(self, image_bytes: bytes) -> Tuple[str, float, dict]:
        """
        Devuelve (label, confidence, details).
        Si ML está deshabilitado/no disponible, devuelve un resultado dummy seguro.
        """
        if not self.enabled or not TORCH_AVAILABLE:
            return "UNKNOWN", 0.5, {
                "prob_ai": 0.5,
                "prob_real": 0.5,
                "threshold": float(settings.PIXELCHECK_THRESHOLD),
                "model_version": settings.PIXELCHECK_MODEL_VERSION,
                "metadata": self.metadata,
                "features": {},
                "observations": {},
            }

        pil_img = Image.open(BytesIO(image_bytes)).convert("RGBA")
        tensor = self.transform(pil_img.convert("RGB")).unsqueeze(0).to(self.device)

        with torch.no_grad():
            logits = self.model(tensor)
            probs = torch.softmax(logits, dim=1)[0]

        prob_ai = float(probs[self.ai_index])
        prob_real = float(probs[1 - self.ai_index]) if probs.numel() > 1 else 1.0 - prob_ai
        threshold = float(settings.PIXELCHECK_THRESHOLD)

        label = "AI" if prob_ai >= threshold else "REAL"
        confidence = prob_ai if label == "AI" else prob_real
        features = self._compute_simple_features(pil_img)
        observations = self._build_observations(features)
        details = {
            "prob_ai": prob_ai,
            "prob_real": prob_real,
            "threshold": threshold,
            "model_version": settings.PIXELCHECK_MODEL_VERSION,
            "metadata": self.metadata,
            "features": features,
            "observations": observations,
        }
        return label, confidence, details

    def _compute_simple_features(self, img: Image.Image) -> dict:
        """Heurísticas rápidas para features amigables a la UI."""
        rgb_img = img.convert("RGB")
        arr = np.asarray(rgb_img, dtype=np.float32) / 255.0
        h, w, _ = arr.shape

        uniq_colors = len(np.unique(arr.reshape(-1, 3), axis=0))
        color_score = float(min(1.0, uniq_colors / max(1, (h * w / 10_000))))

        if img.mode == "RGBA":
            alpha = np.asarray(img.getchannel("A"), dtype=np.float32) / 255.0
            transparency_score = float(max(0.0, 1.0 - alpha.mean()))
        else:
            transparency_score = 0.0

        gray = np.dot(arr[..., :3], [0.299, 0.587, 0.114])
        noise_raw = float(np.std(gray))
        noise_score = float(min(1.0, noise_raw * 2.5))

        high_freq = np.abs(np.diff(gray, axis=0)).mean() + np.abs(np.diff(gray, axis=1)).mean()
        watermark_score = float(min(1.0, high_freq * 2.0))

        mid = w // 2
        left = arr[:, :mid, :]
        right = np.fliplr(arr[:, -mid:, :])
        sym_diff = float(np.mean(np.abs(left - right)))
        symmetry_score = float(max(0.0, 1.0 - sym_diff * 2.0))

        return {
            "color_score": round(color_score, 2),
            "transparency_score": round(transparency_score, 2),
            "noise_score": round(noise_score, 2),
            "watermark_score": round(watermark_score, 2),
            "symmetry_score": round(symmetry_score, 2),
        }

    def _build_observations(self, features: dict) -> dict:
        return {
            "colors": f"Diversidad cromática estimada {int(features['color_score']*100)}%",
            "noise": f"Nivel de ruido {int(features['noise_score']*100)}%",
            "watermark": f"Huellas de marca {int(features['watermark_score']*100)}%",
            "symmetry": f"Simetría {int(features['symmetry_score']*100)}%",
            "transparency": f"Opacidad estimada {int((1 - features['transparency_score'])*100)}%",
        }
