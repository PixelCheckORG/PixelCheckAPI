from django.http import HttpResponse
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from results.application.use_cases import CreateReportUseCase, GetReportFileUseCase
from results.infrastructure.repositories import DjangoReportRepository, DjangoResultsQueryRepository
from results.interface.serializers.result_serializers import ReportRequestSerializer
from shared.application.permissions import IsProfessional


class CreateReportView(APIView):
    permission_classes = [IsProfessional]

    def post(self, request):
        serializer = ReportRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        use_case = CreateReportUseCase(DjangoResultsQueryRepository(), DjangoReportRepository())
        result = use_case.execute(
            requester=request.user,
            image_id=str(data["imageId"]),
            report_format=data["format"],
        )
        return Response(result.data, status=status.HTTP_202_ACCEPTED)


class ReportDownloadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, report_id):
        use_case = GetReportFileUseCase(DjangoReportRepository())
        result = use_case.execute(requester=request.user, report_id=str(report_id))
        payload = result.data
        response = HttpResponse(payload["content"], content_type=payload["content_type"])
        response["Content-Disposition"] = f'attachment; filename="{payload["filename"]}"'
        return response
