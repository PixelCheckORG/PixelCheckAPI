import hashlib
from io import BytesIO
from typing import BinaryIO

from django.conf import settings
from PIL import Image

from shared.domain.exceptions import ValidationError

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_DIMENSION = 4096


def ensure_valid_image(uploaded_file) -> Image.Image:
    if uploaded_file.content_type not in ALLOWED_MIME_TYPES:
        raise ValidationError("Formato de imagen no soportado")
    if uploaded_file.size > settings.DATA_UPLOAD_MAX_MEMORY_SIZE:
        raise ValidationError("Imagen excede el tamaño permitido")

    data = uploaded_file.read()
    uploaded_file.seek(0)

    try:
        image = Image.open(BytesIO(data))
        image.verify()
    except Exception as exc:
        raise ValidationError("Archivo no es una imagen válida") from exc

    image = Image.open(BytesIO(data))
    width, height = image.size
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise ValidationError("Dimensiones de imagen excedidas")
    return image


def calculate_checksum(stream: BinaryIO) -> str:
    sha256 = hashlib.sha256()
    for chunk in iter(lambda: stream.read(8192), b""):
        sha256.update(chunk)
    stream.seek(0)
    return sha256.hexdigest()
