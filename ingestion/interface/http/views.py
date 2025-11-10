from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from ingestion.application.use_cases import UploadImageUseCase
from ingestion.infrastructure.repositories import DjangoImageRepository
from ingestion.interface.serializers.upload import UploadImageSerializer


class UploadImageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = UploadImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        image_file = serializer.validated_data["image"]
        use_case = UploadImageUseCase(DjangoImageRepository())
        result = use_case.execute(uploader=request.user, uploaded_file=image_file)
        return Response(result.data, status=status.HTTP_202_ACCEPTED)
