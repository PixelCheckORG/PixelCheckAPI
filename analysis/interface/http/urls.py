from django.urls import path

from .views import ModelHealthView

urlpatterns = [
    path("health", ModelHealthView.as_view(), name="model-health"),
]
