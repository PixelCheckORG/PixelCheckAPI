from dataclasses import dataclass
from typing import List

from iam.domain.value_objects import RoleNameVO


@dataclass
class RoleEntity:
    name: RoleNameVO
    description: str | None = None


@dataclass
class UserEntity:
    id: str
    email: str | None
    username: str
    roles: List[RoleEntity]
