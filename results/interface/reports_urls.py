from django.urls import path

from .report_views import CreateReportView, ReportDownloadView

urlpatterns = [
    path("", CreateReportView.as_view(), name="create-report"),
    path("<uuid:report_id>", ReportDownloadView.as_view(), name="download-report"),
]
