from django.urls import include, path

urlpatterns = [
    path("auth/", include("iam.interface.http.urls")),
    path("images/", include("ingestion.interface.http.urls")),
    path("results/", include("results.interface.http.urls")),
    path("reports/", include("results.interface.reports_urls")),
    path("analysis/", include("analysis.interface.http.urls")),
    path("system/", include("sysmgmt.interface.http.urls")),
]
