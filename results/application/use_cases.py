from django.utils import timezone

from analysis.models import AnalysisResult
from iam.domain.value_objects import ROLE_PROFESSIONAL
from results.domain.repositories import ReportRepository, ResultsQueryRepository
from results.models import Report
from shared.application.use_case import UseCase, UseCaseResult
from shared.domain.exceptions import NotFoundError, PermissionError
from shared.utils.reporting import build_analysis_pdf, build_csv
from ingestion.models import Image, ImageData


def _can_view_all(user) -> bool:
    if not getattr(user, "is_authenticated", False):
        return True
    return user.has_role(ROLE_PROFESSIONAL) or user.is_staff


class GetResultUseCase(UseCase):
    def __init__(self, repository: ResultsQueryRepository):
        self.repository = repository

    def execute(self, requester, image_id: str) -> UseCaseResult:
        can_view = _can_view_all(requester)
        owner_id = str(requester.id) if getattr(requester, "is_authenticated", False) else None
        entity = self.repository.get_by_image(image_id=image_id, owner_id=owner_id, can_view_all=can_view)
        if not entity:
            raise NotFoundError("Resultado no disponible (en proceso o no existe)")

        include_report = getattr(requester, "is_authenticated", False) and (
            requester.has_role(ROLE_PROFESSIONAL) or requester.is_staff
        )
        return UseCaseResult(
            success=True,
            data={
                "imageId": entity.image_id,
                "label": entity.label,
                "confidence": entity.confidence,
                "modelVersion": entity.model_version,
                "details": entity.details,
                "reportId": self._find_report_for_image(entity.image_id, requester) if include_report else None,
            },
        )

    def _find_report_for_image(self, image_id: str, requester):
        # Busca reportes ya generados para este image_id
        report = Report.objects.filter(filename__contains=image_id, owner=requester).order_by("-created_at").first()
        if report:
            return str(report.report_id)
        return None


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
        # Try to fetch image bytes for embedding
        image_bytes = None
        try:
            image_instance = Image.objects.select_related("data").get(image_id=image_id)
            image_bytes = bytes(image_instance.data.content) if hasattr(image_instance, "data") else None
        except Image.DoesNotExist:
            pass

        conclusion = (result.details or {}).get("conclusion", "N/A")
        recommendation = (
            "La imagen parece auténtica. Continúa con inspección visual si es crítico."
            if result.label == "REAL"
            else "Alta sospecha de generación IA. Recomendado someter a verificación manual adicional."
        )
        features = (result.details or {}).get("features", {})
        observations = (result.details or {}).get("observations", {})

        if report_format == Report.Format.PDF:
            summary = {
                "Etiqueta": result.label,
                "Confianza": f"{result.confidence:.2f}",
                "Modelo": result.model_version,
                "Conclusión": conclusion,
            }
            content = build_analysis_pdf(
                title=f"PixelCheck Report {image_id}",
                summary=summary,
                features=features,
                observations=observations,
                recommendation=recommendation,
                image_bytes=image_bytes,
            )
            return content, "application/pdf", f"pixelcheck-{image_id}-{timestamp}.pdf"
        headers = ["imageId", "label", "confidence", "modelVersion", "conclusion"]
        rows = [
            [
                image_id,
                result.label,
                f"{result.confidence:.2f}",
                result.model_version,
                conclusion,
            ]
        ]
        content = build_csv(headers, rows)
        return content, "text/csv", f"pixelcheck-{image_id}-{timestamp}.csv"


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
