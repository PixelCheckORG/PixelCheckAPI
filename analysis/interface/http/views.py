from django.conf import settings
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView


class ModelHealthView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response(
            {
                "modelVersion": settings.PIXELCHECK_MODEL_VERSION,
                "threshold": settings.PIXELCHECK_THRESHOLD,
            }
        )
