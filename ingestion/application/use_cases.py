from analysis.tasks import run_analysis_task
from ingestion.domain.repositories import ImageRepository
from ingestion.models import Image
from shared.application.use_case import UseCase, UseCaseResult
from shared.domain.exceptions import ValidationError
from shared.utils.image import calculate_checksum, ensure_valid_image


class UploadImageUseCase(UseCase):
    def __init__(self, repository: ImageRepository):
        self.repository = repository

    def execute(self, uploader, uploaded_file):
        image = ensure_valid_image(uploaded_file)
        checksum = calculate_checksum(uploaded_file.file)
        binary_data = uploaded_file.read()
        payload = {
            "uploader": uploader,
            "filename": uploaded_file.name,
            "mime_type": uploaded_file.content_type,
            "size_bytes": uploaded_file.size,
            "width": image.width,
            "height": image.height,
            "checksum": checksum,
            "status": Image.Status.QUEUED,
            "binary_data": binary_data,
        }
        entity = self.repository.create(**payload)
        run_analysis_task.delay(str(entity.image_id))
        return UseCaseResult(success=True, data={"imageId": entity.image_id, "status": entity.status})
