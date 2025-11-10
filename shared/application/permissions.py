from rest_framework.permissions import BasePermission

from iam.domain.value_objects import ROLE_PROFESSIONAL


class IsProfessional(BasePermission):
    message = "Se requiere rol ROLE_PROFESSIONAL o staff."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.has_role(ROLE_PROFESSIONAL) or user.is_staff
