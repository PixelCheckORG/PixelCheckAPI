from decimal import Decimal

from django.conf import settings

from analysis.domain.repositories import AnalysisResultRepository
from ingestion.models import Image
from shared.application.use_case import UseCase, UseCaseResult
from shared.domain.exceptions import NotFoundError


class AnalyzeImageUseCase(UseCase):
    def __init__(self, repository: AnalysisResultRepository):
        self.repository = repository

    def execute(self, image_id: str) -> UseCaseResult:
        try:
            image = Image.objects.select_related("uploader", "data").get(image_id=image_id)
        except Image.DoesNotExist as exc:
            raise NotFoundError("Imagen no encontrada") from exc

        checksum_value = int(image.checksum[:4], 16)
        label = "AI" if checksum_value % 2 == 0 else "REAL"
        confidence = Decimal(checksum_value % 100) / Decimal(100)

        entity = self.repository.save_result(
            image=image,
            owner=image.uploader,
            label=label,
            confidence=confidence,
            model_version=settings.PIXELCHECK_MODEL_VERSION,
        )
        image.status = Image.Status.DONE
        image.save(update_fields=["status"])
        return UseCaseResult(success=True, data=entity)
