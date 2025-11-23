from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from results.application.use_cases import GetResultUseCase
from results.infrastructure.repositories import DjangoResultsQueryRepository
from results.interface.serializers.result_serializers import ImageResultSerializer


class ResultDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ImageResultSerializer

    @extend_schema(
        responses={200: ImageResultSerializer},
        tags=["results"],
    )
    def get(self, request, image_id):
        use_case = GetResultUseCase(DjangoResultsQueryRepository())
        result = use_case.execute(requester=request.user, image_id=str(image_id))
        return Response(result.data, status=status.HTTP_200_OK)
