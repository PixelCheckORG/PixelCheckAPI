import uuid

from django.conf import settings
from django.db import models


class Report(models.Model):
    class Scope(models.TextChoices):
        SINGLE = "SINGLE"
        BATCH = "BATCH"

    class Format(models.TextChoices):
        PDF = "PDF"
        CSV = "CSV"

    class Status(models.TextChoices):
        REQUESTED = "REQUESTED"
        GENERATING = "GENERATING"
        READY = "READY"
        FAILED = "FAILED"

    report_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reports"
    )
    scope = models.CharField(max_length=16, choices=Scope.choices, default=Scope.SINGLE)
    format = models.CharField(max_length=8, choices=Format.choices, default=Format.PDF)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.REQUESTED)
    created_at = models.DateTimeField(auto_now_add=True)
    filename = models.CharField(max_length=255, blank=True)
    content = models.BinaryField(null=True, blank=True)
    content_mime = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ("-created_at",)
