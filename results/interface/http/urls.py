from django.urls import path

from .views import ResultDetailView

urlpatterns = [
    path("<uuid:image_id>", ResultDetailView.as_view(), name="result-detail"),
]
