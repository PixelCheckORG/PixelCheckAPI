from django.http import HttpResponse
from django.http import HttpResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import permissions
from rest_framework.views import APIView

from results.application.use_cases import GetReportFileUseCase
from results.infrastructure.repositories import DjangoReportRepository


class ReportDownloadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: OpenApiResponse(response=OpenApiTypes.BINARY, description="Archivo de reporte")},
        tags=["reports"],
    )
    def get(self, request, report_id):
        use_case = GetReportFileUseCase(DjangoReportRepository())
        result = use_case.execute(requester=request.user, report_id=str(report_id))
        payload = result.data
        response = HttpResponse(payload["content"], content_type=payload["content_type"])
        response["Content-Disposition"] = f'attachment; filename="{payload["filename"]}"'
        return response
