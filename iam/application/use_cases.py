from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from shared.application.use_case import UseCase, UseCaseResult
from shared.domain.exceptions import ValidationError

from iam.domain.repositories import UserRepository


class RegisterUserUseCase(UseCase):
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def execute(self, email: str, username: str, password: str) -> UseCaseResult:
        if self.repository.get_by_email(email):
            return UseCaseResult(success=False, error="Email ya registrado")
        user = self.repository.create_user(email=email, username=username, password=password)
        return UseCaseResult(success=True, data=user)


class SignInUseCase(UseCase):
    def execute(self, email: str, password: str) -> UseCaseResult:
        user = authenticate(username=email, password=password)
        if not user:
            raise ValidationError("Credenciales inválidas")
        refresh = RefreshToken.for_user(user)
        payload = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "roles": list(user.roles.values_list("name", flat=True)),
            },
        }
        return UseCaseResult(success=True, data=payload)
