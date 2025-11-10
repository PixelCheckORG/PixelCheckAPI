from django.utils import timezone

from analysis.models import AnalysisResult
from iam.domain.value_objects import ROLE_PROFESSIONAL
from results.domain.repositories import ReportRepository, ResultsQueryRepository
from results.models import Report
from shared.application.use_case import UseCase, UseCaseResult
from shared.domain.exceptions import NotFoundError, PermissionError
from shared.utils.reporting import build_csv, build_pdf


def _can_view_all(user) -> bool:
    return user.has_role(ROLE_PROFESSIONAL) or user.is_staff


class GetResultUseCase(UseCase):
    def __init__(self, repository: ResultsQueryRepository):
        self.repository = repository

    def execute(self, requester, image_id: str) -> UseCaseResult:
        can_view = _can_view_all(requester)
        entity = self.repository.get_by_image(image_id=image_id, owner_id=str(requester.id), can_view_all=can_view)
        if not entity:
            raise NotFoundError("Resultado no disponible")
        return UseCaseResult(
            success=True,
            data={
                "imageId": entity.image_id,
                "label": entity.label,
                "confidence": entity.confidence,
                "modelVersion": entity.model_version,
            },
        )


class CreateReportUseCase(UseCase):
    def __init__(self, results_repo: ResultsQueryRepository, report_repo: ReportRepository):
        self.results_repo = results_repo
        self.report_repo = report_repo

    def execute(self, requester, image_id: str, report_format: str) -> UseCaseResult:
        if not requester.has_role(ROLE_PROFESSIONAL) and not requester.is_staff:
            raise PermissionError("Se requiere ROLE_PROFESSIONAL para crear reportes")
        result = self.results_repo.get_by_image(
            image_id=image_id, owner_id=str(requester.id), can_view_all=True
        )
        if not result:
            raise NotFoundError("Resultado no encontrado")

        report = self.report_repo.create_report(
            owner=requester,
            scope=Report.Scope.SINGLE,
            format=report_format,
            status=Report.Status.GENERATING,
        )

        content, mime, filename = self._build_content(result, report_format, image_id)
        self.report_repo.update_report(
            report_id=report.report_id,
            status=Report.Status.READY,
            filename=filename,
            content=content,
            content_mime=mime,
        )
        return UseCaseResult(success=True, data={"reportId": report.report_id})

    def _build_content(self, result, report_format, image_id):
        timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
        if report_format == Report.Format.PDF:
            payload = {
                "title": f"PixelCheck Report {image_id}",
                "Image": image_id,
                "Label": result.label,
                "Confidence": f"{result.confidence:.2f}",
                "Model": result.model_version,
            }
            content = build_pdf(payload)
            return content, "application/pdf", f"pixelcheck-{timestamp}.pdf"
        headers = ["imageId", "label", "confidence", "modelVersion"]
        rows = [[image_id, result.label, f"{result.confidence:.2f}", result.model_version]]
        content = build_csv(headers, rows)
        return content, "text/csv", f"pixelcheck-{timestamp}.csv"


class GetReportFileUseCase(UseCase):
    def __init__(self, report_repo: ReportRepository):
        self.report_repo = report_repo

    def execute(self, requester, report_id: str) -> UseCaseResult:
        can_view = _can_view_all(requester)
        report = self.report_repo.get_report(
            report_id=report_id, owner_id=str(requester.id), can_view_all=can_view
        )
        if not report:
            raise NotFoundError("Reporte no encontrado")
        instance = Report.objects.get(report_id=report.report_id)
        if instance.status != Report.Status.READY:
            raise NotFoundError("Reporte aún no está listo")
        return UseCaseResult(
            success=True,
            data={
                "filename": instance.filename,
                "content": bytes(instance.content),
                "content_type": instance.content_mime,
            },
        )
