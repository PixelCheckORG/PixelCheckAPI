from dataclasses import dataclass

from shared.domain.exceptions import ValidationError

ROLE_USER = "ROLE_USER"
ROLE_PROFESSIONAL = "ROLE_PROFESSIONAL"
ALLOWED_ROLES = {ROLE_USER, ROLE_PROFESSIONAL}


@dataclass(frozen=True)
class RoleNameVO:
    value: str

    def __post_init__(self) -> None:
        if self.value not in ALLOWED_ROLES:
            raise ValidationError("Rol no soportado para PixelCheck")

    def __str__(self) -> str:
        return self.value
