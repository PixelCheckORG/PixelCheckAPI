from rest_framework import serializers


class AuditLogSerializer(serializers.Serializer):
    action = serializers.CharField(max_length=128)
    target = serializers.CharField(max_length=128, allow_blank=True, required=False)
    payload = serializers.JSONField(required=False)


class AuditLogEntrySerializer(serializers.Serializer):
    log_id = serializers.UUIDField()
    actor_id = serializers.CharField(allow_null=True)
    action = serializers.CharField()
    target = serializers.CharField()
    payload = serializers.JSONField()
    occurred_at = serializers.DateTimeField()
