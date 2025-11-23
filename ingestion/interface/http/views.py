from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model
from rest_framework import permissions, serializers, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from ingestion.application.use_cases import UploadImageUseCase
from ingestion.infrastructure.repositories import DjangoImageRepository
from ingestion.interface.serializers.upload import (
    UploadImageResponseSerializer,
    UploadImageSerializer,
)


class UploadImageView(APIView):
    # Permitir uploads anónimos; si no hay usuario autenticado, se usa un invitado.
    permission_classes = [permissions.AllowAny]
    serializer_class = UploadImageSerializer
    parser_classes = (MultiPartParser, FormParser)

    @extend_schema(
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "image": {"type": "string", "format": "binary"},
                },
                "required": ["image"],
            }
        },
        responses={202: UploadImageResponseSerializer},
        tags=["images"],
    )
    def post(self, request):
        serializer = UploadImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        image_file = serializer.validated_data["image"]

        # Si no hay usuario autenticado, usamos/creamos un usuario invitado para registrar la imagen.
        if request.user.is_authenticated:
            uploader = request.user
        else:
            User = get_user_model()
            uploader, created = User.objects.get_or_create(
                username="guest",
                defaults={"email": None, "is_active": True},
            )
            if created:
                uploader.set_unusable_password()
                uploader.save(update_fields=["password"])

        use_case = UploadImageUseCase(DjangoImageRepository())
        result = use_case.execute(uploader=uploader, uploaded_file=image_file)
        return Response(result.data, status=status.HTTP_202_ACCEPTED)
