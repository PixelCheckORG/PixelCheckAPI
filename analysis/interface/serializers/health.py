from rest_framework import serializers


class ModelHealthSerializer(serializers.Serializer):
    modelVersion = serializers.CharField()
    threshold = serializers.FloatField()
