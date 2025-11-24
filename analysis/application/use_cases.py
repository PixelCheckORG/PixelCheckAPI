from decimal import Decimal

from django.conf import settings

from analysis.domain.repositories import AnalysisResultRepository
from analysis.ml.inference import PixelCheckInference
from ingestion.models import Image
from results.application.use_cases import CreateReportUseCase
from results.infrastructure.repositories import DjangoReportRepository, DjangoResultsQueryRepository
from shared.application.use_case import UseCase, UseCaseResult
from shared.domain.exceptions import NotFoundError
from iam.domain.value_objects import ROLE_PROFESSIONAL


class AnalyzeImageUseCase(UseCase):
    def __init__(self, repository: AnalysisResultRepository):
        self.repository = repository
        self.inference = PixelCheckInference.instance()

    def execute(self, image_id: str) -> UseCaseResult:
        try:
            image = Image.objects.select_related("uploader", "data").get(image_id=image_id)
        except Image.DoesNotExist as exc:
            raise NotFoundError("Imagen no encontrada") from exc

        # Carga el binario de la imagen y ejecuta inferencia real
        image_bytes = bytes(image.data.content)
        label, confidence_float, details = self.inference.predict(image_bytes)
        confidence = Decimal(str(confidence_float))

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
