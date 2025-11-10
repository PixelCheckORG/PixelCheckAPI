from abc import ABC, abstractmethod
from typing import Optional

from .entities import UserEntity


class UserRepository(ABC):
    @abstractmethod
    def create_user(self, email: str, username: str, password: str) -> UserEntity: ...

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[UserEntity]: ...
