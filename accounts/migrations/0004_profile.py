"""Профиль пользователя (Тема 13): связь 1:1 с User, каскадное удаление."""
import accounts.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_resettoken_indexes'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='Телефон')),
                ('group_name', models.CharField(blank=True, max_length=40, verbose_name='Учебная группа')),
                ('bio', models.TextField(blank=True, verbose_name='О себе')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создан')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Профиль пользователя',
                'verbose_name_plural': 'Профили пользователей',
            },
        ),
    ]
