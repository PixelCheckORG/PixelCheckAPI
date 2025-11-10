from django.contrib import admin

from .models import AnalysisResult


@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    list_display = ("result_id", "image", "label", "confidence", "model_version", "processed_at")
    list_filter = ("label", "model_version")
