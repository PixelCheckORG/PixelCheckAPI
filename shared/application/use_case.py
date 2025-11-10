from dataclasses import dataclass
from typing import Generic, Optional, TypeVar


T = TypeVar("T")


@dataclass
class UseCaseResult(Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None


class UseCase:
    def execute(self, *args, **kwargs) -> UseCaseResult:
        raise NotImplementedError
