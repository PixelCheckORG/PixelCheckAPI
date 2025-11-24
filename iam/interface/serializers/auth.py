from rest_framework import serializers


from iam.domain.value_objects import ALLOWED_ROLES


class SignUpSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=64)
    password = serializers.CharField(min_length=8, write_only=True)
    roles = serializers.ListField(
        child=serializers.ChoiceField(choices=sorted(ALLOWED_ROLES)),
        allow_empty=False,
    )


class SignInSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=64)
    password = serializers.CharField(write_only=True)


class SignInResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    user = serializers.DictField()


class SignUpResponseSerializer(serializers.Serializer):
    userId = serializers.UUIDField()
    roles = serializers.ListField(child=serializers.CharField())
