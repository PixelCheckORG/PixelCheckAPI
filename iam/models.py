import uuid

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from iam.domain.value_objects import ROLE_PROFESSIONAL, ROLE_USER


class Role(models.Model):
    class RoleName(models.TextChoices):
        USER = ROLE_USER, "User"
        PROFESSIONAL = ROLE_PROFESSIONAL, "Professional"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=32, unique=True, choices=RoleName.choices)
    description = models.CharField(max_length=128, blank=True)

    def __str__(self) -> str:
        return self.name


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, password, email=None, **extra_fields):
        email = self.normalize_email(email) if email else None
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, email=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username=username, password=password, email=email, **extra_fields)

    def create_superuser(self, username, password=None, email=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser debe tener is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser debe tener is_superuser=True.")
        return self._create_user(username=username, password=password, email=email, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, null=True, blank=True)
    username = models.CharField(max_length=64, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    roles = models.ManyToManyField(Role, related_name="users", blank=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.username

    def has_role(self, role_name: str) -> bool:
        return self.roles.filter(name=role_name).exists()

    @property
    def is_professional(self) -> bool:
        return self.has_role(Role.RoleName.PROFESSIONAL)
