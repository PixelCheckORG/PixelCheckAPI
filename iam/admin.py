from django.contrib import admin

from .models import Role, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "username", "is_active", "is_staff", "created_at")
    list_filter = ("is_active", "is_staff", "roles")
    search_fields = ("email", "username")
    filter_horizontal = ("roles",)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
