"""
Модель бронирования (Темы 4, 5, 8, 9).
Серверная проверка пересечений интервалов — функция check_conflict.
"""
import datetime as dt

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from rooms.models import Room

BLOCKING_STATUSES = None  # задаётся ниже


class Booking(models.Model):
    """Бронирование аудитории пользователем."""

    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_REJECTED = 'rejected'
    STATUS_CANCELLED = 'cancelled'
    STATUS_COMPLETED = 'completed'
    STATUS_CHOICES = (
        (STATUS_PENDING, 'Ожидает подтверждения'),
        (STATUS_CONFIRMED, 'Подтверждено'),
        (STATUS_REJECTED, 'Отклонено'),
        (STATUS_CANCELLED, 'Отменено'),
        (STATUS_COMPLETED, 'Завершено'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='bookings', verbose_name='Пользователь'
    )
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name='bookings', verbose_name='Аудитория'
    )
    date = models.DateField('Дата')
    time_start = models.TimeField('Время начала')
    time_end = models.TimeField('Время окончания')
    purpose = models.CharField('Цель бронирования', max_length=200)
    comment = models.TextField('Комментарий', blank=True)
    status = models.CharField(
        'Статус', max_length=12, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        ordering = ('-date', '-time_start')
        indexes = [
            models.Index(fields=['room', 'date']),
            models.Index(fields=['user', 'date']),
            models.Index(fields=['status']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(time_end__gt=models.F('time_start')),
                name='booking_time_end_after_start',
            ),
        ]

    @staticmethod
    def blocking_statuses():
        return [Booking.STATUS_PENDING, Booking.STATUS_CONFIRMED]

    def conflicts_with_existing(self, exclude_pk=None):
        """
        Проверка пересечения интервалов (Тема 8):
        частичное пересечение, вложенные интервалы, границы.
        Интервалы пересекаются, если start < other.end И end > other.start.
        """
        qs = Booking.objects.filter(
            room=self.room,
            date=self.date,
            status__in=self.blocking_statuses(),
            time_start__lt=self.time_end,
            time_end__gt=self.time_start,
        )
        if exclude_pk:
            qs = qs.exclude(pk=exclude_pk)
        return qs

    def clean(self):
        if self.time_start and self.time_end and self.time_start >= self.time_end:
            raise ValidationError('Время окончания должно быть позже времени начала.')
        if self.date and self.date < dt.date.today() and self.pk is None:
            raise ValidationError('Нельзя бронировать на прошедшую дату.')
        if self.room_id and not self.room.is_available():
            raise ValidationError('Аудитория недоступна для бронирования.')

    def save(self, *args, **kwargs):
        self.full_clean(exclude=[] if self.pk else ['date'])
        if not self.pk and self.conflicts_with_existing().exists():
            raise ValidationError('Аудитория уже занята в выбранное время.')
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.room} — {self.date} {self.time_start}–{self.time_end} ({self.get_status_display()})'
