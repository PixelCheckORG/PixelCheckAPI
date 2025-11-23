from rest_framework import serializers


class UploadImageSerializer(serializers.Serializer):
    image = serializers.ImageField(use_url=False)


class UploadImageResponseSerializer(serializers.Serializer):
    imageId = serializers.UUIDField()
    status = serializers.CharField()
