"""
Модель истории диалога с ИИ-агентом (Тема 14).

Каждое сообщение — одна реплика диалога: либо реплика пользователя,
либо ответ агента. История хранится в PostgreSQL и передаётся модели
при каждом следующем запросе (признак «агента», а не простой обёртки).
"""
from django.conf import settings as dj_settings
from django.db import models


class AiMessage(models.Model):
    """Сообщение диалога пользователя с ИИ-агентом."""

    ROLE_USER = 'user'
    ROLE_ASSISTANT = 'assistant'
    ROLE_CHOICES = (
        (ROLE_USER, 'Реплика пользователя'),
        (ROLE_ASSISTANT, 'Ответ агента'),
    )

    user = models.ForeignKey(
        dj_settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_messages',
        verbose_name='Пользователь',
    )
    role = models.CharField('Роль реплики', max_length=10, choices=ROLE_CHOICES)
    content = models.TextField('Текст сообщения')
    created_at = models.DateTimeField('Создано', auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'Сообщение ИИ-агента'
        verbose_name_plural = 'Сообщения ИИ-агента'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['user', 'created_at'], name='ai_user_created_idx'),
        ]

    def __str__(self):
        return f'{self.user_id}: {self.role}: {self.content[:40]}'

    @classmethod
    def history_for(cls, user, limit=20):
        """Последние сообщения диалога пользователя (для контекста модели)."""
        return list(
            cls.objects.filter(user=user)
            .order_by('-created_at')
            .values('role', 'content')[:limit][::-1]
        )
