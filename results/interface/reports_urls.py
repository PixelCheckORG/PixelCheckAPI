from django.urls import path

from .report_views import ReportDownloadView

urlpatterns = [
    path("<uuid:report_id>", ReportDownloadView.as_view(), name="download-report"),
]
