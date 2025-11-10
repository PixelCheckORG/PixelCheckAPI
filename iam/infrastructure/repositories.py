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
    def create_user(self, email: str, username: str, password: str) -> UserEntity:
        user = User.objects.create_user(email=email, username=username, password=password)
        default_role, _ = Role.objects.get_or_create(name=Role.RoleName.USER)
        user.roles.add(default_role)
        return _to_user_entity(user)

    def get_by_email(self, email: str) -> UserEntity | None:
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None
        return _to_user_entity(user)
