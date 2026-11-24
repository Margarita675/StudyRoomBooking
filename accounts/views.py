"""
Представления приложения accounts (Темы 6, 7, 8).
Регистрация, вход, выход, профиль, восстановление пароля по email.
"""
import secrets
from smtplib import SMTPException

from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse

from .decorators import admin_required
from .forms import (
    ForgotPasswordForm,
    LoginForm,
    ProfileForm,
    RegisterForm,
    ResetPasswordForm,
)
from .models import PasswordResetToken, User


def register_view(request):
    if request.user.is_authenticated:
        return redirect('rooms:list')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешна. Добро пожаловать в StudyRoomBooking!')
            return redirect('rooms:list')
        messages.error(request, 'Исправьте ошибки в форме.')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('rooms:list')
    if request.method == 'POST':
        data = request.POST.copy()
        # Вход по email или username (Тема 6, шаг 2.1)
        identifier = data.get('username', '')
        if '@' in identifier:
            user_by_email = User.objects.filter(email__iexact=identifier).first()
            if user_by_email:
                data['username'] = user_by_email.username
        form = LoginForm(request, data=data)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Вы вошли в систему.')
            return redirect(request.GET.get('next') or 'rooms:list')
        messages.error(request, 'Неверные учётные данные.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    context = {
        'pets_count': request.user.pets.count(),
        'entries_count': sum(p.entries.count() for p in request.user.pets.all()),
        'procedures_count': sum(p.procedures.count() for p in request.user.pets.all()),
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён.')
            return redirect('accounts:profile')
        messages.error(request, 'Исправьте ошибки в форме.')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/profile_edit.html', {'form': form})


# ---------------- Тема 7. Восстановление пароля ----------------

def forgot_password_view(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()
            if user:
                raw_token = secrets.token_urlsafe(32)
                hashed_token = PasswordResetToken.hash_token(raw_token)
                # Инвалидация старых токенов
                PasswordResetToken.objects.filter(user=user, is_used=False).update(is_used=True)
                PasswordResetToken.objects.create(user=user, token_hash=hashed_token)
                reset_url = request.build_absolute_uri(
                    reverse('accounts:reset_password', kwargs={'token': raw_token})
                )
                try:
                    send_mail(
                        'Восстановление пароля StudyRoomBooking',
                        f'Для сброса пароля перейдите по ссылке:\n{reset_url}\n\n'
                        f'Ссылка действительна {PasswordResetToken.TOKEN_TTL_MINUTES} минут.',
                        None,  # DEFAULT_FROM_EMAIL из settings
                        [user.email],
                        fail_silently=False,
                    )
                except SMTPException as e:
                    print(f'Ошибка отправки письма: {e}')
                    messages.error(request, 'Произошла ошибка при отправке письма. Попробуйте позже.')
                    return redirect('accounts:forgot_password')
            # Защита от перебора email: единый нейтральный ответ
            messages.success(request, 'Если аккаунт с таким email существует, письмо отправлено.')
            return redirect('accounts:login')
    else:
        form = ForgotPasswordForm()
    return render(request, 'accounts/forgot_password.html', {'form': form})


def reset_password_view(request, token):
    hashed_token = PasswordResetToken.hash_token(token)
    reset_token = PasswordResetToken.objects.filter(token_hash=hashed_token, is_used=False).first()
    if not reset_token or not reset_token.is_valid():
        messages.error(request, 'Ссылка недействительна или истёк её срок действия.')
        return redirect('accounts:login')

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user = reset_token.user
            user.set_password(form.cleaned_data['password'])  # хеширование средствами Django
            user.save()
            reset_token.is_used = True  # одноразовость токена
            reset_token.save()
            messages.success(request, 'Пароль успешно изменён. Войдите с новым паролем.')
            return redirect('accounts:login')
    else:
        form = ResetPasswordForm()
    return render(request, 'accounts/reset_password.html', {'form': form, 'token': token})


@admin_required
def admin_dashboard_view(request):
    """Панель управления пользователями (Тема 8, матрица прав)."""
    users = User.objects.order_by('-date_joined')
    return render(request, 'accounts/admin_dashboard.html', {'users': users})


@login_required
def admin_block_user_view(request, user_id):
    """Блокировка/разблокировка аккаунта — только admin (Тема 8, 3.4.3)."""
    if not request.user.is_admin():
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied('Доступ только для администратора')
    target = User.objects.get(pk=user_id)
    if target.is_superuser:
        messages.error(request, 'Нельзя блокировать суперпользователя.')
    elif target == request.user:
        messages.error(request, 'Нельзя заблокировать свой аккаунт.')
    else:
        target.is_active = not target.is_active
        target.save(update_fields=['is_active'])
        messages.success(request, f'Аккаунт {target.username} {"разблокирован" if target.is_active else "заблокирован"}.')
    return redirect('accounts:admin_dashboard')


@login_required
def admin_delete_user_view(request, user_id):
    """Удаление пользователя (кроме суперпользователя) — только admin."""
    if not request.user.is_admin():
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied('Доступ только для администратора')
    target = User.objects.get(pk=user_id)
    if target.is_superuser:
        messages.error(request, 'Нельзя удалить суперпользователя.')
    elif target == request.user:
        messages.error(request, 'Нельзя удалить свой аккаунт.')
    else:
        username = target.username
        target.delete()
        messages.success(request, f'Пользователь {username} удалён.')
    return redirect('accounts:admin_dashboard')


def home_view(request):
    """Главная страница (Тема 9-10-11)."""
    from rooms.models import Room
    return render(request, 'home.html', {'rooms': Room.objects.filter(
        status=Room.STATUS_ACTIVE)[:6]})
