from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from analysis.interface.serializers.health import ModelHealthSerializer


class ModelHealthView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ModelHealthSerializer

    @extend_schema(
        responses={200: ModelHealthSerializer},
        tags=["analysis"],
    )
    def get(self, request):
        return Response(
            {
                "modelVersion": settings.PIXELCHECK_MODEL_VERSION,
                "threshold": settings.PIXELCHECK_THRESHOLD,
            }
        )
