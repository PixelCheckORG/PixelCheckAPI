from drf_spectacular.utils import extend_schema
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
    permission_classes = [permissions.IsAuthenticated]
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
        use_case = UploadImageUseCase(DjangoImageRepository())
        result = use_case.execute(uploader=request.user, uploaded_file=image_file)
        return Response(result.data, status=status.HTTP_202_ACCEPTED)
