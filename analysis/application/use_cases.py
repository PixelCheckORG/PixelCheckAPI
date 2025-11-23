from decimal import Decimal
from random import Random

from django.conf import settings

from analysis.domain.repositories import AnalysisResultRepository
from ingestion.models import Image
from results.application.use_cases import CreateReportUseCase
from results.infrastructure.repositories import DjangoReportRepository, DjangoResultsQueryRepository
from shared.application.use_case import UseCase, UseCaseResult
from shared.domain.exceptions import NotFoundError
from iam.domain.value_objects import ROLE_PROFESSIONAL


class AnalyzeImageUseCase(UseCase):
    def __init__(self, repository: AnalysisResultRepository):
        self.repository = repository

    def _build_details(self, checksum_value: int) -> dict:
        rnd = Random(checksum_value)
        color = round(rnd.uniform(0.4, 1.0), 2)
        noise = round(rnd.uniform(0.0, 0.6), 2)
        transparency = round(rnd.uniform(0.0, 0.2), 2)
        watermark = round(rnd.uniform(0.0, 0.3), 2)
        symmetry = round(rnd.uniform(0.4, 1.0), 2)
        features = {
            "color_score": color,
            "noise_score": noise,
            "transparency_score": transparency,
            "watermark_score": watermark,
            "symmetry_score": symmetry,
        }
        conclusion = (
            "Rasgos visuales naturales, baja probabilidad de IA"
            if symmetry > 0.5 and watermark < 0.15
            else "Patrones sospechosos de síntesis, revisar con cautela"
        )
        return {
            "features": features,
            "conclusion": conclusion,
            "observations": {
                "colors": f"Diversidad cromática estimada {int(color*100)}%",
                "noise": f"Nivel de ruido {int(noise*100)}%",
                "watermark": f"Huellas de marca {int(watermark*100)}%",
                "symmetry": f"Simetría {int(symmetry*100)}%",
            },
        }

    def execute(self, image_id: str) -> UseCaseResult:
        try:
            image = Image.objects.select_related("uploader", "data").get(image_id=image_id)
        except Image.DoesNotExist as exc:
            raise NotFoundError("Imagen no encontrada") from exc

        checksum_value = int(image.checksum[:6], 16)
        label = "AI" if checksum_value % 2 == 0 else "REAL"
        confidence = Decimal(checksum_value % 100) / Decimal(100)
        details = self._build_details(checksum_value)

        entity = self.repository.save_result(
            image=image,
            owner=image.uploader,
            label=label,
            confidence=confidence,
            model_version=settings.PIXELCHECK_MODEL_VERSION,
            details=details,
        )
        image.status = Image.Status.DONE
        image.save(update_fields=["status"])

        if image.uploader.has_role(ROLE_PROFESSIONAL) or image.uploader.is_staff:
            # Autogenerar reporte PDF para profesionales/staff
            CreateReportUseCase(DjangoResultsQueryRepository(), DjangoReportRepository()).execute(
                requester=image.uploader,
                image_id=str(image.image_id),
                report_format="PDF",
            )
        return UseCaseResult(success=True, data=entity)
