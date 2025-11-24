from abc import ABC, abstractmethod
from typing import Optional

from .entities import UserEntity


class UserRepository(ABC):
    @abstractmethod
    def create_user(self, username: str, password: str, roles: list[str]) -> UserEntity: ...

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[UserEntity]: ...
