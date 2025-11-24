from iam.domain.entities import RoleEntity, UserEntity
from iam.domain.repositories import UserRepository
from iam.domain.value_objects import RoleNameVO
from iam.models import Role, User


def _to_role_entity(role: Role) -> RoleEntity:
    return RoleEntity(name=RoleNameVO(role.name), description=role.description)


def _to_user_entity(user: User) -> UserEntity:
    roles = [_to_role_entity(role) for role in user.roles.all()]
    return UserEntity(id=str(user.id), email=user.email, username=user.username, roles=roles)


class DjangoUserRepository(UserRepository):
    def create_user(self, username: str, password: str, roles: list[str]) -> UserEntity:
        user = User.objects.create_user(username=username, password=password)
        roles_to_set = roles or [Role.RoleName.USER]
        role_objs = []
        for role_name in roles_to_set:
            role_obj, _ = Role.objects.get_or_create(name=role_name)
            role_objs.append(role_obj)
        user.roles.add(*role_objs)
        return _to_user_entity(user)

    def get_by_username(self, username: str) -> UserEntity | None:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        return _to_user_entity(user)
