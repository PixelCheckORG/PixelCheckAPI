from rest_framework import serializers


class AuditLogSerializer(serializers.Serializer):
    action = serializers.CharField(max_length=128)
    target = serializers.CharField(max_length=128, allow_blank=True, required=False)
    payload = serializers.JSONField(required=False)
