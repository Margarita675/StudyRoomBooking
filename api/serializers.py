"""
Сериализаторы REST API (Тема 12).
Валидация бронирования (включая пересечения) выполняется на сервере.
"""
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from accounts.models import User
from bookings.models import Booking
from rooms.models import Equipment, Room, RoomEquipment


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Пользователь с таким email уже существует.')
        return value

    def create(self, validated_data):
        return User.objects.create_user(role=User.ROLE_USER, **validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'full_name')


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = ('id', 'name', 'description')


class RoomSerializer(serializers.ModelSerializer):
    equipment = serializers.SerializerMethodField()
    room_type_display = serializers.CharField(source='get_room_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Room
        fields = ('id', 'number', 'name', 'building', 'floor', 'capacity',
                  'room_type', 'room_type_display', 'status', 'status_display',
                  'description', 'photo', 'equipment')
        read_only_fields = ('photo',)

    def get_equipment(self, obj):
        return [{'id': re.equipment_id, 'name': re.equipment.name, 'quantity': re.quantity}
                for re in obj.room_equipment.select_related('equipment')]


class RoomWriteSerializer(serializers.ModelSerializer):
    equipment_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, write_only=True)

    class Meta:
        model = Room
        fields = ('number', 'name', 'building', 'floor', 'capacity',
                  'room_type', 'status', 'description', 'equipment_ids')

    def create(self, validated_data):
        ids = validated_data.pop('equipment_ids', [])
        room = Room.objects.create(**validated_data)
        room.equipment.set(Equipment.objects.filter(pk__in=ids))
        return room

    def update(self, instance, validated_data):
        ids = validated_data.pop('equipment_ids', None)
        room = super().update(instance, validated_data)
        if ids is not None:
            room.equipment.set(Equipment.objects.filter(pk__in=ids))
        return room


class BookingSerializer(serializers.ModelSerializer):
    room_number = serializers.CharField(source='room.number', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Booking
        fields = ('id', 'room', 'room_number', 'room_name', 'user', 'user_name',
                  'date', 'time_start', 'time_end', 'purpose', 'comment',
                  'status', 'status_display', 'created_at')
        read_only_fields = ('user', 'status', 'created_at')

    def validate_date(self, value):
        from django.utils import timezone
        if value < timezone.localdate():
            raise serializers.ValidationError('Нельзя бронировать на прошедшую дату.')
        return value

    def validate(self, attrs):
        start, end = attrs.get('time_start'), attrs.get('time_end')
        if start and end and start >= end:
            raise serializers.ValidationError(
                {'time_end': 'Время окончания должно быть позже времени начала.'})
        room = attrs.get('room')
        if room and not room.is_available():
            raise serializers.ValidationError(
                {'room': 'Аудитория недоступна для бронирования.'})
        return attrs

    def create(self, validated_data):
        booking = Booking(**validated_data)
        if booking.conflicts_with_existing().exists():
            raise serializers.ValidationError(
                {'time_start': 'Аудитория уже занята в выбранное время (пересечение броней).'})
        booking.save()
        return booking
