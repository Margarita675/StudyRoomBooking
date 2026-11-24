"""
Модели приложения accounts (Темы 4, 6, 7, 8).

User — расширенная модель пользователя с полем role (RBAC).
PasswordResetToken — таблица одноразовых токенов восстановления пароля
(в БД хранится только SHA-256 хеш токена, Тема 7).
"""
import hashlib
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Пользователь системы с ролевой моделью доступа (RBAC)."""

    ROLE_USER = 'user'
    ROLE_ADMIN = 'admin'
    ROLE_CHOICES = (
        (ROLE_USER, 'Пользователь'),
        (ROLE_ADMIN, 'Администратор'),
    )

    # Email обязателен и уникален (Тема 6, шаг 1.2)
    email = models.EmailField('Email', unique=True)
    role = models.CharField('Роль', max_length=10, choices=ROLE_CHOICES, default=ROLE_USER)
    full_name = models.CharField('ФИО', max_length=150, blank=True)
    created_at = models.DateTimeField('Дата регистрации', auto_now_add=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def is_admin(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser


class Profile(models.Model):
    """Профиль пользователя (Тема 13): связь 1:1 с User (CASCADE)."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile', verbose_name='Пользователь'
    )
    phone = models.CharField('Телефон', max_length=20, blank=True)
    group_name = models.CharField('Учебная группа', max_length=40, blank=True)
    bio = models.TextField('О себе', blank=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f'Профиль: {self.user.username}'


class PasswordResetToken(models.Model):
    """Одноразовый токен восстановления пароля (Тема 7)."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reset_tokens', verbose_name='Пользователь'
    )
    # В БД хранится ТОЛЬКО хеш SHA-256, а не сам токен
    token_hash = models.CharField('Хеш токена (SHA-256)', max_length=64, unique=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    expires_at = models.DateTimeField('Истекает')
    is_used = models.BooleanField('Использован', default=False)

    TOKEN_TTL_MINUTES = 30

    class Meta:
        verbose_name = 'Токен восстановления пароля'
        verbose_name_plural = 'Токены восстановления пароля'

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=self.TOKEN_TTL_MINUTES)
        super().save(*args, **kwargs)

    def is_valid(self):
        """Токен действителен, если не использован и не истёк."""
        return not self.is_used and self.expires_at > timezone.now()

    @staticmethod
    def hash_token(raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode()).hexdigest()

    def __str__(self):
        return f'Токен для {self.user.username} (использован: {self.is_used})'
