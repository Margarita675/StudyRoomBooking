"""
Представления приложения rooms (Темы 5, 6, 9, 11).
Список, карточка аудитории, поиск свободных аудиторий по параметрам,
CRUD для администратора.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import admin_required

from bookings.models import Booking
from .forms import EquipmentForm, RoomForm
from .models import Equipment, Room


def room_list_view(request):
    """Список аудиторий (Тема 9) с фильтрами по корпусу, типу и вместимости."""
    rooms = Room.objects.all().prefetch_related('equipment')
    building = request.GET.get('building', '').strip()
    room_type = request.GET.get('room_type', '')
    min_capacity = request.GET.get('min_capacity', '').strip()
    if building:
        rooms = rooms.filter(building__iexact=building)
    if room_type:
        rooms = rooms.filter(room_type=room_type)
    if min_capacity.isdigit():
        rooms = rooms.filter(capacity__gte=int(min_capacity))
    paginator = Paginator(rooms, 9)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'rooms/list.html', {
        'page_obj': page,
        'buildings': Room.objects.values_list('building', flat=True).distinct().order_by('building'),
        'types': Room.TYPE_CHOICES,
        'filters': request.GET,
    })


def room_detail_view(request, room_id):
    """Карточка аудитории: характеристики, оборудование, занятость на сегодня."""
    room = get_object_or_404(Room.objects.prefetch_related('equipment'), pk=room_id)
    today = timezone.localdate()
    day_bookings = (Booking.objects.filter(room=room, date=today)
                    .exclude(status__in=[Booking.STATUS_CANCELLED, Booking.STATUS_REJECTED])
                    .order_by('time_start'))
    return render(request, 'rooms/detail.html', {
        'room': room,
        'day_bookings': day_bookings,
        'today': today,
    })


def _filter_rooms(request, qs):
    """Общие фильтры поиска: вместимость, тип, корпус, оборудование."""
    capacity = request.GET.get('capacity', '').strip()
    room_type = request.GET.get('room_type', '')
    building = request.GET.get('building', '').strip()
    equipment_ids = [v for v in request.GET.getlist('equipment') if v.isdigit()]
    if capacity.isdigit() and int(capacity) > 0:
        qs = qs.filter(capacity__gte=int(capacity))
    if room_type:
        qs = qs.filter(room_type=room_type)
    if building:
        qs = qs.filter(building__iexact=building)
    if equipment_ids:
        for eq_id in equipment_ids:
            qs = qs.filter(equipment__pk=eq_id)  # каждое выбранное оборудование должно быть
    return qs.distinct(), equipment_ids


def _exclude_busy(qs, date, time_start, time_end):
    """Исключает аудитории, занятые активными бронями в указанный интервал."""
    busy = (Booking.objects.filter(room__in=qs, date=date,
                                   status__in=[Booking.STATUS_PENDING, Booking.STATUS_CONFIRMED])
            .filter(time_start__lt=time_end, time_end__gt=time_start)
            .values_list('room_id', flat=True))
    return qs.exclude(pk__in=list(busy))


def room_search_view(request):
    """
    Поиск свободных аудиторий (Тема 9): дата, время, вместимость,
    тип, корпус, оборудование. Только серверная фильтрация.
    """
    rooms = Room.objects.filter(status=Room.STATUS_ACTIVE)
    date = request.GET.get('date', '').strip()
    time_start = request.GET.get('time_start', '').strip()
    time_end = request.GET.get('time_end', '').strip()
    searched = bool(request.GET)
    results = None
    error = None
    if searched:
        if not date:
            error = 'Укажите дату.'
        elif not (time_start and time_end):
            error = 'Укажите время начала и окончания.'
        else:
            try:
                import datetime as dt
                d = dt.date.fromisoformat(date)
                ts = dt.time.fromisoformat(time_start)
                te = dt.time.fromisoformat(time_end)
            except ValueError:
                error = 'Некорректная дата или время.'
            if not error and ts >= te:
                error = 'Время окончания должно быть позже времени начала.'
            if not error and d < timezone.localdate():
                error = 'Нельзя искать в прошедшей дате.'
            if not error:
                rooms, _ = _filter_rooms(request, rooms)
                results = _exclude_busy(rooms, d, ts, te)
    else:
        results = rooms
    return render(request, 'rooms/search.html', {
        'results': results,
        'searched': searched,
        'error': error,
        'equipment_list': Equipment.objects.all(),
        'types': Room.TYPE_CHOICES,
        'buildings': Room.objects.values_list('building', flat=True).distinct().order_by('building'),
        'today': timezone.localdate().isoformat(),
    })


@admin_required
def room_create_view(request):
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            room = form.save()
            room.equipment.set(form.cleaned_data['equipment_rows'])
            messages.success(request, 'Аудитория добавлена.')
            return redirect('rooms:detail', room.pk)
        messages.error(request, 'Исправьте ошибки в форме.')
    else:
        form = RoomForm()
    return render(request, 'rooms/form.html', {'form': form, 'title': 'Новая аудитория'})


@admin_required
def room_edit_view(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            room = form.save()
            room.equipment.set(form.cleaned_data['equipment_rows'])
            messages.success(request, 'Изменения сохранены.')
            return redirect('rooms:detail', room.pk)
        messages.error(request, 'Исправьте ошибки в форме.')
    else:
        initial = {'equipment_rows': room.equipment.all()}
        form = RoomForm(instance=room, initial=initial)
    return render(request, 'rooms/form.html', {'form': form, 'title': f'Редактирование: {room}'})


@admin_required
def room_delete_view(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    if request.method == 'POST':
        room.delete()
        messages.success(request, 'Аудитория удалена.')
        return redirect('rooms:list')
    return render(request, 'rooms/confirm_delete.html', {'room': room})


@admin_required
def equipment_list_view(request):
    """Каталог оборудования (Тема 6) — управление администратором."""
    equipment = Equipment.objects.prefetch_related('rooms').all()
    return render(request, 'rooms/equipment_list.html', {'equipment_list': equipment})


@admin_required
def equipment_create_view(request):
    if request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Оборудование добавлено.')
            return redirect('rooms:equipment')
        messages.error(request, 'Исправьте ошибки в форме.')
    else:
        form = EquipmentForm()
    return render(request, 'rooms/equipment_form.html', {'form': form, 'title': 'Новое оборудование'})


@admin_required
def equipment_edit_view(request, equipment_id):
    obj = get_object_or_404(Equipment, pk=equipment_id)
    if request.method == 'POST':
        form = EquipmentForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Оборудование обновлено.')
            return redirect('rooms:equipment')
        messages.error(request, 'Исправьте ошибки в форме.')
    else:
        form = EquipmentForm(instance=obj)
    return render(request, 'rooms/equipment_form.html', {'form': form, 'title': f'Редактирование: {obj}'})


@admin_required
def equipment_delete_view(request, equipment_id):
    obj = get_object_or_404(Equipment, pk=equipment_id)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Оборудование удалено.')
        return redirect('rooms:equipment')
    return render(request, 'rooms/equipment_confirm_delete.html', {'obj': obj})
