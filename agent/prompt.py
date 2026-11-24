"""
Системный промпт ИИ-агента StudyRoomBooking (Тема 14, раздел 7).

Агент отличается от «просто чата» тремя признаками:
1) системный промпт с ролью и правилами поведения в приложении;
2) контекст из БД — агент знает, кто с ним говорит и что происходит
   в приложении (аудитории, бронирования пользователя);
3) история диалога, передаваемая модели при каждом запросе.
"""
from datetime import date

from django.contrib.auth import get_user_model

from bookings.models import Booking
from rooms.models import Equipment, Room

STATUS_LABELS = dict(Booking.STATUS_CHOICES)
TYPE_LABELS = dict(Room.TYPE_CHOICES)


def build_context(user):
    """Собирает фактический контекст пользователя из БД (без секретов)."""
    rooms_total = Room.objects.count()
    free_types = (
        [TYPE_LABELS.get(t, t) for t in
         Room.objects.values_list('room_type', flat=True).distinct().order_by()]
    )
    equipment_names = list(
        Equipment.objects.values_list('name', flat=True).order_by('name')[:15]
    )
    my_bookings = (
        Booking.objects.filter(user=user)
        .select_related('room')
        .order_by('-date')[:5]
    )
    my_lines = [
        f"– {b.room.number} от {b.date:%d.%m.%Y} {b.time_start:%H:%M}–{b.time_end:%H:%M} "
        f"({STATUS_LABELS.get(b.status, b.status)})"
        for b in my_bookings
    ] or ['– пока нет бронирований']

    context = (
        f"Текущая дата: {date.today():%d.%m.%Y}.\n"
        f"Пользователь: {user.get_full_name() or user.username} "
        f"(роль: {user.role}).\n"
        f"В системе {rooms_total} аудиторий. Типы аудиторий: "
        f"{', '.join(free_types) or 'нет данных'}.\n"
        f"Оборудование, которое можно искать: {', '.join(equipment_names) or 'нет данных'}.\n"
        "Последние бронирования пользователя:\n" + '\n'.join(my_lines)
    )
    return context


SYSTEM_PROMPT = (
    "Ты — «Помощник StudyRoomBooking», встроенный ИИ-агент системы бронирования "
    "аудиторий колледжа. Твоя задача: помогать студентам находить аудиторию, "
    "объяснять, как оформить бронирование, как посмотреть расписание, как отменить "
    "свою бронь и какие права есть у обычного пользователя и администратора.\n"
    "Правила:\n"
    "1. Отвечай только на русском языке, кратко и по делу (до 5 предложений).\n"
    "2. Опирайся только на функции системы: поиск аудиторий (дата, время, вместимость, "
    "тип, оборудование), бронирование с проверкой конфликтов, расписание, личный "
    "кабинет, подтверждение брони администратором.\n"
    "3. Не выдумывай функции, которых нет, и не давай ссылки на несуществующие страницы.\n"
    "4. Не раскрывай внутренние данные: ключи, пароли, чужие бронирования, SQL-запросы.\n"
    "5. Если пользователь просит что-то вне твоей роли — вежливо верни его к работе "
    "с системой бронирования.\n"
    "6. Не давай гарантий и не обещай действий от имени системы: только подсказывай, "
    "какую страницу и кнопку использовать.\n"
    "7. Конфиденциальные и персональные данные других пользователей не обсуждай.\n"
    "\nКонтекст текущего пользователя и системы:\n{context}"
)


def build_messages(user, history):
    """Формирует массив сообщений для OpenAI-compatible API."""
    return (
        [{'role': 'system', 'content': SYSTEM_PROMPT.format(context=build_context(user))}]
        + [{'role': h['role'], 'content': h['content']} for h in history]
    )
