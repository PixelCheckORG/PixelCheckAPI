from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import AccessToken

from shared.application.use_case import UseCase, UseCaseResult
from shared.domain.exceptions import ValidationError

from iam.domain.repositories import UserRepository


class RegisterUserUseCase(UseCase):
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def execute(self, username: str, password: str, roles: list[str]) -> UseCaseResult:
        if self.repository.get_by_username(username):
            return UseCaseResult(success=False, error="Username ya registrado")
        user = self.repository.create_user(username=username, password=password, roles=roles)
        return UseCaseResult(success=True, data=user)


class SignInUseCase(UseCase):
    def execute(self, username: str, password: str) -> UseCaseResult:
        user = authenticate(username=username, password=password)
        if not user:
            raise ValidationError("Credenciales inválidas")
        access_token = AccessToken.for_user(user)
        payload = {
            "access": str(access_token),
            "user": {
                "id": str(user.id),
                "username": user.username,
                "roles": list(user.roles.values_list("name", flat=True)),
            },
        }
        return UseCaseResult(success=True, data=payload)
