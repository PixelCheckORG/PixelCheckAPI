from django.contrib.auth import get_user_model
from rest_framework import serializers


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=64)
    password = serializers.CharField(min_length=8, write_only=True)

    def validate_email(self, value):
        User = get_user_model()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email ya registrado")
        return value


class SignInSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
