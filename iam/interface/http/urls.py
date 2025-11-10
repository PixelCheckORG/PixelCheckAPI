from django.urls import path

from .views import SignInView, SignUpView

urlpatterns = [
    path("sign-up", SignUpView.as_view(), name="sign-up"),
    path("sign-in", SignInView.as_view(), name="sign-in"),
]
