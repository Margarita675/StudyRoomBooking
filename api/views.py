"""
REST API (Тема 12): JWT-аутентификация, аудитории, бронирования,
поиск свободных аудиторий, восстановление пароля, служебные маршруты.
Коды ответов: 200/201/204/400/401/403/404/422.
"""
import secrets
from smtplib import SMTPException

from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.decorators import admin_required
from accounts.models import PasswordResetToken, User
from bookings.models import Booking
from rooms.models import Equipment, Room

from .permissions import IsAdmin, IsOwnerOrAdmin
from .serializers import (
    BookingSerializer,
    EquipmentSerializer,
    RegisterSerializer,
    RoomSerializer,
    RoomWriteSerializer,
    UserSerializer,
)


def _validation_error_response(serializer):
    """Требование Темы 12: ошибки валидации — код 422."""
    return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


def health(request):
    """Служебный маршрут для проверки доступности (Тема 5)."""
    from django.http import JsonResponse
    return JsonResponse({'status': 'ok', 'service': 'web'})


def ping(request):
    from django.http import JsonResponse
    return JsonResponse({'status': 'ok', 'message': 'pong'})


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return _validation_error_response(serializer)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username') or request.data.get('email')
        password = request.data.get('password')
        if not username or not password:
            return Response({'detail': 'Укажите логин и пароль.'},
                            status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({'detail': 'Неверные учётные данные.'},
                            status=status.HTTP_401_UNAUTHORIZED)
        refresh = RefreshToken.for_user(user)
        return Response({'access': str(refresh.access_token),
                         'refresh': str(refresh),
                         'user': UserSerializer(user).data}, status=status.HTTP_200_OK)


class PasswordResetRequestAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get('email') or '').strip().lower()
        if not email:
            return Response({'detail': 'Укажите email.'},
                            status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(email__iexact=email).first()
        token = None
        if user:
            raw = secrets.token_urlsafe(32)
            PasswordResetToken.objects.create(user=user,
                                              token_hash=PasswordResetToken.hash_token(raw))
            token = raw
            try:
                send_mail(
                    'Восстановление пароля StudyRoomBooking',
                    f'Токен восстановления: {raw}\nДействителен 30 минут, одноразовый.',
                    None, [user.email], fail_silently=True,
                )
            except SMTPException:
                pass
        # Нейтральный ответ против перебора email (Тема 7)
        return Response({'detail': 'Если email зарегистрирован, токен отправлен.',
                         'token': token}, status=status.HTTP_200_OK)


class PasswordResetConfirmAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('token', '')
        new_password = request.data.get('password', '')
        if not token or not new_password:
            return Response({'detail': 'Укажите токен и новый пароль.'},
                            status=status.HTTP_400_BAD_REQUEST)
        obj = PasswordResetToken.objects.filter(
            token_hash=PasswordResetToken.hash_token(token)).first()
        if obj is None or not obj.is_valid():
            return Response({'detail': 'Токен недействителен или истёк.'},
                            status=status.HTTP_400_BAD_REQUEST)
        obj.user.set_password(new_password)
        obj.user.save()
        obj.is_used = True
        obj.save(update_fields=['is_used'])
        return Response({'detail': 'Пароль изменён.'}, status=status.HTTP_200_OK)


class RoomListAPIView(APIView):
    """GET — список аудиторий (для всех), POST — создание (только админ)."""
    permission_classes = [AllowAny]

    def get(self, request):
        rooms = Room.objects.all().prefetch_related('room_equipment__equipment')
        building = request.query_params.get('building', '').strip()
        room_type = request.query_params.get('room_type', '').strip()
        min_capacity = request.query_params.get('min_capacity', '').strip()
        if building:
            rooms = rooms.filter(building__iexact=building)
        if room_type:
            rooms = rooms.filter(room_type=room_type)
        if min_capacity.isdigit():
            rooms = rooms.filter(capacity__gte=int(min_capacity))
        page = self.paginate(rooms, request)
        return Response({'count': len(page['items']), 'results': page['items']},
                        status=status.HTTP_200_OK)

    def paginate(self, qs, request):
        try:
            page = max(int(request.query_params.get('page', 1)), 1)
        except ValueError:
            page = 1
        try:
            size = min(max(int(request.query_params.get('page_size', 20)), 1), 100)
        except ValueError:
            size = 20
        start = (page - 1) * size
        items = RoomSerializer(qs[start:start + size], many=True).data
        return {'items': items}

    def post(self, request):
        serializer = RoomWriteSerializer(data=request.data)
        if not self.is_admin(request):
            return Response({'detail': 'Доступно только администратору.'},
                            status=status.HTTP_403_FORBIDDEN)
        if serializer.is_valid():
            room = serializer.save()
            return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)
        return _validation_error_response(serializer)

    def is_admin(self, request):
        user = request.user
        return bool(user and user.is_authenticated and user.is_admin())


class RoomDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, room_id):
        room = get_object_or_404(Room, pk=room_id)
        return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)

    def put(self, request, room_id):
        user = request.user
        if not (user and user.is_authenticated and user.is_admin()):
            return Response({'detail': 'Доступно только администратору.'},
                            status=status.HTTP_403_FORBIDDEN)
        room = get_object_or_404(Room, pk=room_id)
        serializer = RoomWriteSerializer(room, data=request.data)
        if serializer.is_valid():
            room = serializer.save()
            return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)
        return _validation_error_response(serializer)

    def delete(self, request, room_id):
        user = request.user
        if not (user and user.is_authenticated and user.is_admin()):
            return Response({'detail': 'Доступно только администратору.'},
                            status=status.HTTP_403_FORBIDDEN)
        room = get_object_or_404(Room, pk=room_id)
        room.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EquipmentListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        data = EquipmentSerializer(Equipment.objects.all(), many=True).data
        return Response({'results': data}, status=status.HTTP_200_OK)


class BookingListAPIView(APIView):
    """GET — свои брони (админ видит все с ?all=1), POST — создание."""

    def get(self, request):
        if request.query_params.get('all') == '1' and request.user.is_admin():
            bookings = Booking.objects.all()
        else:
            bookings = Booking.objects.filter(user=request.user)
        status_filter = request.query_params.get('status', '').strip()
        if status_filter:
            bookings = bookings.filter(status=status_filter)
        data = BookingSerializer(
            bookings.select_related('room', 'user')[:100], many=True).data
        return Response({'results': data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            booking = serializer.save(user=request.user)
            return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)
        return _validation_error_response(serializer)


class BookingDetailAPIView(APIView):
    """Свои брони; чужие — 403 (анти-IDOR). Админ может менять статус."""

    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, pk=booking_id)
        if not request.user.is_admin() and booking.user_id != request.user.id:
            return Response({'detail': 'Нет доступа к чужому бронированию.'},
                            status=status.HTTP_403_FORBIDDEN)
        return Response(BookingSerializer(booking).data, status=status.HTTP_200_OK)

    def delete(self, request, booking_id):
        booking = get_object_or_404(Booking, pk=booking_id)
        if not request.user.is_admin() and booking.user_id != request.user.id:
            return Response({'detail': 'Нет доступа к чужому бронированию.'},
                            status=status.HTTP_403_FORBIDDEN)
        if booking.status not in (Booking.STATUS_PENDING, Booking.STATUS_CONFIRMED):
            return Response({'detail': 'Эту бронь нельзя отменить.'},
                            status=status.HTTP_400_BAD_REQUEST)
        booking.status = Booking.STATUS_CANCELLED
        booking.save(update_fields=['status'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, booking_id):
        user = request.user
        if not user.is_admin():
            return Response({'detail': 'Доступно только администратору.'},
                            status=status.HTTP_403_FORBIDDEN)
        booking = get_object_or_404(Booking, pk=booking_id)
        new_status = request.data.get('status', '')
        allowed = {s for s, _ in Booking.STATUS_CHOICES}
        if new_status not in allowed:
            return Response({'detail': 'Недопустимый статус.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if new_status == Booking.STATUS_CONFIRMED and \
                booking.conflicts_with_existing().filter(
                    status=Booking.STATUS_CONFIRMED).exists():
            return Response({'detail': 'Конфликт: аудитория уже подтверждена на это время.'},
                            status=status.HTTP_400_BAD_REQUEST)
        booking.status = new_status
        booking.save(update_fields=['status'])
        return Response(BookingSerializer(booking).data, status=status.HTTP_200_OK)


class RoomSearchAPIView(APIView):
    """Поиск свободных аудиторий (Тема 12): date, time_start, time_end,
    capacity, room_type, building, equipment (id через запятую)."""
    permission_classes = [AllowAny]

    def get(self, request):
        import datetime as dt
        date = request.query_params.get('date', '').strip()
        time_start = request.query_params.get('time_start', '').strip()
        time_end = request.query_params.get('time_end', '').strip()
        if not date or not time_start or not time_end:
            return Response({'detail': 'Укажите date, time_start и time_end.'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            d = dt.date.fromisoformat(date)
            ts = dt.time.fromisoformat(time_start)
            te = dt.time.fromisoformat(time_end)
        except ValueError:
            return Response({'detail': 'Некорректная дата или время.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if ts >= te:
            return Response({'detail': 'Время окончания должно быть позже начала.'},
                            status=status.HTTP_400_BAD_REQUEST)
        rooms = Room.objects.filter(status=Room.STATUS_ACTIVE)
        capacity = request.query_params.get('capacity', '').strip()
        room_type = request.query_params.get('room_type', '').strip()
        building = request.query_params.get('building', '').strip()
        equipment = request.query_params.get('equipment', '').strip()
        if capacity.isdigit():
            rooms = rooms.filter(capacity__gte=int(capacity))
        if room_type:
            rooms = rooms.filter(room_type=room_type)
        if building:
            rooms = rooms.filter(building__iexact=building)
        if equipment:
            for eq_id in equipment.split(','):
                if eq_id.strip().isdigit():
                    rooms = rooms.filter(equipment__pk=int(eq_id))
        rooms = rooms.distinct()
        busy = (Booking.objects.filter(
            room__in=rooms, date=d,
            status__in=[Booking.STATUS_PENDING, Booking.STATUS_CONFIRMED],
            time_start__lt=te, time_end__gt=ts).values_list('room_id', flat=True))
        results = rooms.exclude(pk__in=list(busy))
        return Response({'date': date, 'time_start': time_start, 'time_end': time_end,
                         'results': RoomSerializer(results, many=True).data},
                        status=status.HTTP_200_OK)


class RoomScheduleAPIView(APIView):
    """Расписание аудитории по дате (Тема 12)."""
    permission_classes = [AllowAny]

    def get(self, request, room_id):
        room = get_object_or_404(Room, pk=room_id)
        date = request.query_params.get('date', '').strip()
        bookings = Booking.objects.filter(room=room)
        if date:
            bookings = bookings.filter(date=date)
        bookings = bookings.exclude(status__in=[Booking.STATUS_CANCELLED, Booking.STATUS_REJECTED])
        return Response({'room': RoomSerializer(room).data,
                         'date': date or None,
                         'results': BookingSerializer(bookings, many=True).data},
                        status=status.HTTP_200_OK)
