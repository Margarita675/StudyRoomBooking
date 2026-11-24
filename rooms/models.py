"""
Модели приложения rooms (Темы 4, 5, 6).

Room — аудитория: корпус, этаж, вместимость, тип, статус.
Equipment — каталог оборудования.
RoomEquipment — нормализованная связь M:N с количеством единиц
(список оборудования не хранится строкой).
"""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Equipment(models.Model):
    """Каталог оборудования (Тема 6)."""

    name = models.CharField('Название', max_length=100, unique=True)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Оборудование'
        verbose_name_plural = 'Оборудование'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Room(models.Model):
    """Аудитория (Тема 5)."""

    TYPE_LECTURE = 'lecture'
    TYPE_COMPUTER = 'computer'
    TYPE_LAB = 'lab'
    TYPE_CONF = 'conference'
    TYPE_CLASS = 'classroom'
    TYPE_UNIVERSAL = 'universal'
    TYPE_CHOICES = (
        (TYPE_LECTURE, 'Лекционная'),
        (TYPE_COMPUTER, 'Компьютерная'),
        (TYPE_LAB, 'Лабораторная'),
        (TYPE_CONF, 'Конференц-зал'),
        (TYPE_CLASS, 'Учебная'),
        (TYPE_UNIVERSAL, 'Универсальная'),
    )

    STATUS_ACTIVE = 'active'
    STATUS_MAINTENANCE = 'maintenance'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = (
        (STATUS_ACTIVE, 'Доступна'),
        (STATUS_MAINTENANCE, 'На обслуживании'),
        (STATUS_CLOSED, 'Закрыта'),
    )

    number = models.CharField('Номер аудитории', max_length=20, unique=True)
    name = models.CharField('Название', max_length=100)
    building = models.CharField('Корпус', max_length=50, default='1')
    floor = models.PositiveSmallIntegerField('Этаж', default=1)
    capacity = models.PositiveSmallIntegerField('Вместимость', default=10)
    room_type = models.CharField(
        'Тип аудитории', max_length=15, choices=TYPE_CHOICES, default=TYPE_CLASS
    )
    status = models.CharField(
        'Статус', max_length=15, choices=STATUS_CHOICES, default=STATUS_ACTIVE
    )
    description = models.TextField('Описание', blank=True)
    photo = models.ImageField('Фотография', upload_to='rooms/', blank=True, null=True)
    created_at = models.DateTimeField('Создана', auto_now_add=True)

    equipment = models.ManyToManyField(
        Equipment, through='RoomEquipment', related_name='rooms', verbose_name='Оборудование'
    )

    class Meta:
        verbose_name = 'Аудитория'
        verbose_name_plural = 'Аудитории'
        ordering = ('building', 'floor', 'number')
        indexes = [
            models.Index(fields=['building', 'floor']),
            models.Index(fields=['capacity']),
            models.Index(fields=['room_type']),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(floor__gte=0), name='room_floor_gte_0'),
            models.CheckConstraint(check=models.Q(capacity__gt=0), name='room_capacity_gt_0'),
        ]

    def is_available(self):
        return self.status == self.STATUS_ACTIVE

    def __str__(self):
        return f'{self.building}-{self.number} «{self.name}»'


class RoomEquipment(models.Model):
    """Связь аудитория–оборудование с количеством единиц."""

    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name='room_equipment', verbose_name='Аудитория'
    )
    equipment = models.ForeignKey(
        Equipment, on_delete=models.CASCADE, related_name='room_links', verbose_name='Оборудование'
    )
    quantity = models.PositiveSmallIntegerField('Количество', default=1)

    class Meta:
        verbose_name = 'Оборудование аудитории'
        verbose_name_plural = 'Оборудование аудиторий'
        unique_together = (('room', 'equipment'),)
        constraints = [
            models.CheckConstraint(check=models.Q(quantity__gt=0), name='room_equipment_qty_gt_0'),
        ]

    def clean(self):
        if self.room_id and self.equipment_id and \
                RoomEquipment.objects.exclude(pk=self.pk).filter(
                    room_id=self.room_id, equipment_id=self.equipment_id).exists():
            raise ValidationError('Такое оборудование уже есть у этой аудитории.')

    def __str__(self):
        return f'{self.room} — {self.equipment} ({self.quantity} шт.)'
