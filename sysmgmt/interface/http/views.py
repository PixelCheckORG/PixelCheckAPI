from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from sysmgmt.application.use_cases import ListAuditLogsUseCase, RecordAuditEventUseCase
from sysmgmt.infrastructure.repositories import DjangoAuditLogRepository
from sysmgmt.interface.serializers.audit import AuditLogEntrySerializer, AuditLogSerializer


class AuditLogView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=AuditLogSerializer,
        responses={201: AuditLogEntrySerializer},
        tags=["system"],
    )
    def post(self, request):
        serializer = AuditLogSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        use_case = RecordAuditEventUseCase(DjangoAuditLogRepository())
        result = use_case.execute(
            actor=request.user,
            action=serializer.validated_data["action"],
            target=serializer.validated_data.get("target", ""),
            payload=serializer.validated_data.get("payload", {}),
        )
        return Response(result.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        responses={200: AuditLogEntrySerializer(many=True)},
        tags=["system"],
    )
    def get(self, request):
        if not request.user.is_staff:
            raise PermissionDenied("Solo administradores pueden ver auditoría")
        use_case = ListAuditLogsUseCase(DjangoAuditLogRepository())
        result = use_case.execute(limit=int(request.query_params.get("limit", 50)))
        return Response(result.data)
