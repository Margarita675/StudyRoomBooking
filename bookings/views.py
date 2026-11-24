"""
Представления приложения bookings (Темы 8, 9, 10, 11).
Личный кабинет, оформление брони, отмена, расписание, управление админом.
Защита от IDOR: пользователь видит и отменяет только свои брони.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import admin_required
from rooms.models import Room

from .forms import BookingForm
from .models import Booking


@login_required
def booking_create_view(request, room_id):
    """Оформление бронирования с серверной проверкой конфликтов (Тема 8)."""
    room = get_object_or_404(Room, pk=room_id)
    if not room.is_available():
        messages.error(request, 'Аудитория недоступна для бронирования.')
        return redirect('rooms:detail', room.pk)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.room = room
            try:
                booking.save()
            except Exception as exc:  # ValidationError из save()/clean()
                messages.error(request, str(getattr(exc, 'message', exc) or exc))
            else:
                messages.success(
                    request,
                    'Бронь создана и ожидает подтверждения администратора.')
                return redirect('bookings:my')
    else:
        form = BookingForm(initial={'room': room})
    return render(request, 'bookings/form.html', {'form': form, 'room': room})


@login_required
def my_bookings_view(request):
    """Личный кабинет (Тема 10): брони пользователя со статусами."""
    status = request.GET.get('status', '')
    bookings = Booking.objects.filter(user=request.user).select_related('room')
    if status:
        bookings = bookings.filter(status=status)
    return render(request, 'bookings/my.html', {
        'bookings': bookings,
        'statuses': Booking.STATUS_CHOICES,
        'current_status': status,
    })


@login_required
def booking_cancel_view(request, booking_id):
    """Отмена своей брони (Тема 10). Чужие брони недоступны (IDOR)."""
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    if request.method == 'POST':
        if booking.status in (Booking.STATUS_PENDING, Booking.STATUS_CONFIRMED):
            booking.status = Booking.STATUS_CANCELLED
            booking.save(update_fields=['status'])
            messages.success(request, 'Бронирование отменено.')
        else:
            messages.error(request, 'Эту бронь нельзя отменить.')
    return render(request, 'bookings/cancel_confirm.html', {'booking': booking})


@login_required
def booking_detail_view(request, booking_id):
    booking = get_object_or_404(Booking.objects.select_related('room'), pk=booking_id,
                                user=request.user)
    return render(request, 'bookings/detail.html', {'booking': booking})


def schedule_view(request):
    """Расписание (Тема 9): фильтр по дате, аудитории, статусу; таблица."""
    date = request.GET.get('date', '')
    room_id = request.GET.get('room', '')
    status = request.GET.get('status', '')
    bookings = Booking.objects.select_related('room', 'user')
    if date:
        bookings = bookings.filter(date=date)
    if room_id.isdigit():
        bookings = bookings.filter(room_id=int(room_id))
    if status:
        bookings = bookings.filter(status=status)
    return render(request, 'bookings/schedule.html', {
        'bookings': bookings,
        'rooms': Room.objects.all(),
        'statuses': Booking.STATUS_CHOICES,
        'today': None,
    })


@admin_required
def admin_bookings_view(request):
    """Управление бронированиями (Тема 11): подтверждение/отклонение."""
    status = request.GET.get('status', '')
    bookings = Booking.objects.select_related('room', 'user')
    if status:
        bookings = bookings.filter(status=status)
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        action = request.POST.get('action')
        booking = Booking.objects.filter(pk=booking_id).first()
        if booking:
            if action == 'confirm' and booking.status == Booking.STATUS_PENDING:
                conflict = booking.conflicts_with_existing()
                if conflict.filter(status=Booking.STATUS_CONFIRMED).exists():
                    messages.error(request, 'Конфликт: аудитория уже подтверждена на это время.')
                else:
                    booking.status = Booking.STATUS_CONFIRMED
                    booking.save(update_fields=['status'])
                    messages.success(request, 'Бронирование подтверждено.')
            elif action == 'reject' and booking.status == Booking.STATUS_PENDING:
                booking.status = Booking.STATUS_REJECTED
                booking.save(update_fields=['status'])
                messages.success(request, 'Бронирование отклонено.')
            elif action == 'cancel':
                booking.status = Booking.STATUS_CANCELLED
                booking.save(update_fields=['status'])
                messages.success(request, 'Бронирование отменено.')
        return redirect('bookings:admin')
    return render(request, 'bookings/admin.html', {
        'bookings': bookings,
        'statuses': Booking.STATUS_CHOICES,
        'current_status': status,
    })


@admin_required
def admin_schedule_view(request, room_id):
    """Расписание конкретной аудитории для администратора."""
    room = get_object_or_404(Room, pk=room_id)
    date = request.GET.get('date', '')
    bookings = Booking.objects.filter(room=room)
    if date:
        bookings = bookings.filter(date=date)
    return render(request, 'bookings/room_schedule.html', {
        'room': room,
        'bookings': bookings.order_by('date', 'time_start'),
        'filter_date': date,
    })
