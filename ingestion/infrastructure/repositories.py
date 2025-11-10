from typing import Iterable

from ingestion.domain.entities import ImageEntity
from ingestion.domain.repositories import ImageRepository
from ingestion.models import Image, ImageData


def _to_entity(image: Image) -> ImageEntity:
    return ImageEntity(
        image_id=str(image.image_id),
        uploader_id=str(image.uploader_id),
        filename=image.filename,
        mime_type=image.mime_type,
        size_bytes=image.size_bytes,
        width=image.width,
        height=image.height,
        checksum=image.checksum,
        status=image.status,
    )


class DjangoImageRepository(ImageRepository):
    def create(self, **kwargs) -> ImageEntity:
        data = kwargs.pop("binary_data")
        image = Image.objects.create(**kwargs)
        ImageData.objects.create(image=image, content=data)
        return _to_entity(image)

    def get(self, image_id: str) -> ImageEntity | None:
        try:
            image = Image.objects.get(image_id=image_id)
        except Image.DoesNotExist:
            return None
        return _to_entity(image)

    def exists_checksum(self, checksum: str, uploader_id: str) -> bool:
        return Image.objects.filter(checksum=checksum, uploader_id=uploader_id).exists()

    def list_by_uploader(self, uploader_id: str) -> Iterable[ImageEntity]:
        for image in Image.objects.filter(uploader_id=uploader_id).order_by("-created_at"):
            yield _to_entity(image)
