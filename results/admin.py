from django.contrib import admin

from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("report_id", "owner", "format", "status", "created_at")
    list_filter = ("format", "status")
    search_fields = ("report_id", "owner__email")
