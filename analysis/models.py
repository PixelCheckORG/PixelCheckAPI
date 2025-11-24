import uuid

from django.conf import settings
from django.db import models


class AnalysisResult(models.Model):
    class Label(models.TextChoices):
        AI = "AI"
        REAL = "REAL"

    result_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.OneToOneField(
        "ingestion.Image", on_delete=models.CASCADE, related_name="analysis_result"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="analysis_results"
    )
    label = models.CharField(max_length=8, choices=Label.choices)
    confidence = models.DecimalField(max_digits=5, decimal_places=4)
    model_version = models.CharField(max_length=64)
    details = models.JSONField(default=dict, blank=True)
    processed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-processed_at",)
