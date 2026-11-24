"""Регистрация модели ИИ-агента в админ-панели."""
from django.contrib import admin

from .models import AiMessage


@admin.register(AiMessage)
class AiMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'short_content', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('content', 'user__username')
    date_hierarchy = 'created_at'

    @admin.display(description='Сообщение')
    def short_content(self, obj):
        return obj.content[:60]
