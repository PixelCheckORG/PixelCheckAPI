from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("log_id", "actor", "action", "target", "occurred_at")
    search_fields = ("action", "target", "actor__email")
