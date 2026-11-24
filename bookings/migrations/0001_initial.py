from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('accounts', '0001_initial'),
        ('rooms', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True,
                     serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Дата')),
                ('time_start', models.TimeField(verbose_name='Время начала')),
                ('time_end', models.TimeField(verbose_name='Время окончания')),
                ('purpose', models.CharField(max_length=200,
                     verbose_name='Цель бронирования')),
                ('comment', models.TextField(blank=True, verbose_name='Комментарий')),
                ('status', models.CharField(choices=[
                     ('pending', 'Ожидает подтверждения'), ('confirmed', 'Подтверждено'),
                     ('rejected', 'Отклонено'), ('cancelled', 'Отменено'),
                     ('completed', 'Завершено')], default='pending', max_length=12,
                     verbose_name='Статус')),
                ('created_at', models.DateTimeField(auto_now_add=True,
                     verbose_name='Создано')),
                ('room', models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='bookings', to='rooms.room',
                     verbose_name='Аудитория')),
                ('user', models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='bookings', to='accounts.user',
                     verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Бронирование', 'verbose_name_plural': 'Бронирования',
                'ordering': ('-date', '-time_start'),
            },
        ),
        migrations.AddIndex(
            model_name='booking', index=models.Index(
                fields=['room', 'date'], name='bookings_room_date_idx')),
        migrations.AddIndex(
            model_name='booking', index=models.Index(
                fields=['user', 'date'], name='bookings_user_date_idx')),
        migrations.AddIndex(
            model_name='booking', index=models.Index(
                fields=['status'], name='bookings_status_idx')),
        migrations.AddConstraint(
            model_name='booking', constraint=models.CheckConstraint(
                check=models.Q(time_end__gt=models.F('time_start')),
                name='booking_time_end_after_start')),
    ]
