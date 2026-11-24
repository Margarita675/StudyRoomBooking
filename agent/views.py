"""
Представления ИИ-агента (Тема 14, разделы 8–10, Django-вариант).

/agent/          — страница чата (только для авторизованных);
/agent/send/     — POST JSON: сохраняет реплику, обращается к провайдеру,
                   сохраняет ответ и возвращает его браузеру;
/agent/clear/    — очистка истории диалога пользователя.

Безопасность (Тема 15): доступ только авторизованным, CSRF-проверка
обязательна, длина сообщения ограничена, ключ провайдера никогда не
покидает сервер, ошибки не раскрывают внутренние детали.
"""
import json

from django.conf import settings as dj_settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .client import AgentNotConfigured, AgentProviderError, chat_completion, is_configured
from .models import AiMessage
from .prompt import build_messages

MAX_MESSAGE_LEN = 2000
MAX_HISTORY = 20

# --- Ограничение частоты запросов (rate limit, Тема 15, раздел 10) ---
# Не более 10 сообщений за 5 минут на пользователя; хранится в памяти процесса
# (для учебного проекта этого достаточно и не требует внешних библиотек).
RATE_LIMIT = 10
RATE_WINDOW = 300  # секунд
_rate_store = {}


def _rate_ok(user_id):
    import time
    now = time.time()
    window = [t for t in _rate_store.get(user_id, []) if now - t < RATE_WINDOW]
    if len(window) >= RATE_LIMIT:
        return False
    window.append(now)
    _rate_store[user_id] = window
    return True


@login_required
def chat_view(request):
    """Страница чата с ИИ-помощником."""
    history = AiMessage.objects.filter(user=request.user)[:MAX_HISTORY]
    return render(request, 'agent/chat.html', {
        'history': history,
        'agent_configured': is_configured(),
        'llm_model': dj_settings.LLM_MODEL,
    })


@login_required
@require_POST
def send_view(request):
    """Обработка одной реплики пользователя (JSON API)."""
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'ok': False, 'error': 'Некорректный JSON в запросе.'}, status=400)

    text = (payload.get('message') or '').strip()
    if not text:
        return JsonResponse({'ok': False, 'error': 'Сообщение пустое.'}, status=400)
    if len(text) > MAX_MESSAGE_LEN:
        return JsonResponse(
            {'ok': False, 'error': f'Сообщение слишком длинное (максимум {MAX_MESSAGE_LEN} символов).'},
            status=400,
        )
    if not _rate_ok(request.user.id):
        return JsonResponse(
            {'ok': False, 'error': 'Слишком много запросов. Подождите несколько минут.'},
            status=429,
        )

    AiMessage.objects.create(user=request.user, role=AiMessage.ROLE_USER, content=text)
    history = AiMessage.history_for(request.user, limit=MAX_HISTORY)

    try:
        answer = chat_completion(build_messages(request.user, history))
    except AgentNotConfigured as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=503)
    except AgentProviderError as exc:
        return JsonResponse(
            {'ok': False, 'error': f'Ошибка ИИ-провайдера: {exc}'}, status=502
        )

    answer = answer[:MAX_MESSAGE_LEN * 2]
    AiMessage.objects.create(user=request.user, role=AiMessage.ROLE_ASSISTANT, content=answer)
    return JsonResponse({'ok': True, 'answer': answer})


@login_required
@require_POST
def clear_view(request):
    """Очистка истории диалога текущего пользователя."""
    AiMessage.objects.filter(user=request.user).delete()
    messages.success(request, 'История диалога с ИИ-помощником очищена.')
    return render(request, 'agent/chat.html', {
        'history': AiMessage.objects.none(),
        'agent_configured': is_configured(),
        'llm_model': dj_settings.LLM_MODEL,
    })
