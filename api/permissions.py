"""Права доступа REST API (Тема 12): RBAC + защита от IDOR."""
from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdmin(BasePermission):
    """Запись/удаление — только администратор."""
    message = 'Доступно только администратору.'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        return bool(user and user.is_authenticated and user.is_admin())


class IsOwnerOrAdmin(BasePermission):
    """Пользователь работает только со своими бронями; админ — со всеми."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        return user.is_admin() or obj.user_id == user.id
