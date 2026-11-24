"""
Декораторы разграничения прав доступа (Тема 8, раздел 3.4.2).

Правило проекта: скрытие кнопок в шаблонах — это только UX.
Любая проверка прав дублируется на сервере.
"""
from functools import wraps

from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def role_required(allowed_roles):
    """Декоратор проверки роли. Неавторизованный → redirect на login,
    неверная роль → 403 Forbidden."""

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.role not in allowed_roles and not request.user.is_superuser:
                raise PermissionDenied  # 403
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator


def admin_required(view_func):
    """Доступ только для администраторов."""
    return role_required(['admin'])(view_func)
