import uuid

from django.conf import settings
from django.db import models


class Image(models.Model):
    class Status(models.TextChoices):
        REJECTED = "REJECTED"
        VALIDATED = "VALIDATED"
        QUEUED = "QUEUED"
        DONE = "DONE"

    image_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="images"
    )
    filename = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=64)
    size_bytes = models.PositiveIntegerField()
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    checksum = models.CharField(max_length=64, db_index=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.QUEUED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.filename} ({self.image_id})"


class ImageData(models.Model):
    image = models.OneToOneField(Image, on_delete=models.CASCADE, related_name="data")
    content = models.BinaryField()
    created_at = models.DateTimeField(auto_now_add=True)
