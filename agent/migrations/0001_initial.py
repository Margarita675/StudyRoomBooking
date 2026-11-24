"""Начальная миграция приложения agent (Тема 14)."""
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AiMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('user', 'Реплика пользователя'), ('assistant', 'Ответ агента')], max_length=10, verbose_name='Роль реплики')),
                ('content', models.TextField(verbose_name='Текст сообщения')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Создано')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ai_messages', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Сообщение ИИ-агента',
                'verbose_name_plural': 'Сообщения ИИ-агента',
                'ordering': ['created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='aimessage',
            index=models.Index(fields=['user', 'created_at'], name='ai_user_created_idx'),
        ),
    ]
