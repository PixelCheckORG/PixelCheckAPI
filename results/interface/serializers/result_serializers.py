from rest_framework import serializers


class ImageResultSerializer(serializers.Serializer):
    label = serializers.CharField()
    confidence = serializers.FloatField()
    modelVersion = serializers.CharField(source="model_version")


class ReportRequestSerializer(serializers.Serializer):
    imageId = serializers.UUIDField()
    format = serializers.ChoiceField(choices=("PDF", "CSV"), default="PDF")
