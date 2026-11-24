"""Тема 13: индексы по полям, по которым идёт поиск (token_hash, is_used, expires_at)."""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_user_email_max_length'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passwordresettoken',
            name='expires_at',
            field=models.DateTimeField(db_index=True, verbose_name='Истекает'),
        ),
        migrations.AddIndex(
            model_name='passwordresettoken',
            index=models.Index(fields=['token_hash', 'is_used'], name='token_lookup_idx'),
        ),
    ]
