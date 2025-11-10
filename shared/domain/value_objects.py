from dataclasses import dataclass

from .exceptions import ValidationError


@dataclass(frozen=True)
class ValueObject:
    value: str

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        raise NotImplementedError

    def __str__(self) -> str:
        return str(self.value)


class EmailVO(ValueObject):
    def _validate(self) -> None:
        if "@" not in self.value:
            raise ValidationError("Email inválido")
