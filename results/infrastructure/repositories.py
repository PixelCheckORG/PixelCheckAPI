from typing import Optional

from analysis.models import AnalysisResult
from ingestion.models import Image
from results.domain.entities import ReportEntity, ResultEntity
from results.domain.repositories import ReportRepository, ResultsQueryRepository
from results.models import Report


def _result_entity(instance: AnalysisResult) -> ResultEntity:
    return ResultEntity(
        image_id=str(instance.image_id),
        label=instance.label,
        confidence=float(instance.confidence),
        model_version=instance.model_version,
        details=instance.details or {},
    )


def _report_entity(instance: Report) -> ReportEntity:
    return ReportEntity(
        report_id=str(instance.report_id),
        owner_id=str(instance.owner_id),
        format=instance.format,
        status=instance.status,
        filename=instance.filename,
    )


class DjangoResultsQueryRepository(ResultsQueryRepository):
    def get_by_image(self, image_id: str, owner_id: str, can_view_all: bool) -> Optional[ResultEntity]:
        qs = AnalysisResult.objects.select_related("image", "owner")
        if not can_view_all:
            qs = qs.filter(owner_id=owner_id)
        try:
            result = qs.get(image_id=image_id)
        except AnalysisResult.DoesNotExist:
            return None
        return _result_entity(result)


class DjangoReportRepository(ReportRepository):
    def create_report(self, **kwargs) -> ReportEntity:
        report = Report.objects.create(**kwargs)
        return _report_entity(report)

    def update_report(self, report_id: str, **kwargs) -> ReportEntity:
        report = Report.objects.get(report_id=report_id)
        for field, value in kwargs.items():
            setattr(report, field, value)
        report.save()
        return _report_entity(report)

    def get_report(self, report_id: str, owner_id: str, can_view_all: bool) -> Optional[ReportEntity]:
        qs = Report.objects.all()
        if not can_view_all:
            qs = qs.filter(owner_id=owner_id)
        try:
            report = qs.get(report_id=report_id)
        except Report.DoesNotExist:
            return None
        return _report_entity(report)
