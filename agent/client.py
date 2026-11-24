"""
Клиент к ИИ-провайдеру (Тема 14).

Поддерживаются оба бесплатных варианта из методички через один и тот же
OpenAI-compatible протокол:
  A) Ollama локально   — LLM_BASE_URL=http://localhost:11434/v1, ключ не нужен;
  B) OpenRouter облако — LLM_BASE_URL=https://openrouter.ai/api/v1,
                         LLM_API_KEY — ключ из личного кабинета.

Ключ хранится ТОЛЬКО в .env (переменная LLM_API_KEY), в БД не попадает.
Запрос выполняется стандартной библиотекой urllib — без новых зависимостей.
"""
import json
import urllib.error
import urllib.request

from django.conf import settings

DEFAULT_TIMEOUT = 60  # секунд


class AgentNotConfigured(Exception):
    """LLM_BASE_URL / LLM_MODEL не заданы в .env."""


class AgentProviderError(Exception):
    """Провайдер вернул ошибку (сеть, лимит, неверный ключ)."""


def is_configured():
    return bool(settings.LLM_BASE_URL and settings.LLM_MODEL)


def chat_completion(messages, max_tokens=600, temperature=0.7):
    """Отправляет историю диалога провайдеру и возвращает текст ответа модели."""
    if not is_configured():
        raise AgentNotConfigured(
            'ИИ-агент не настроен: заполните LLM_BASE_URL, LLM_MODEL '
            '(и LLM_API_KEY для OpenRouter) в файле .env и перезапустите сервер.'
        )

    payload = {
        'model': settings.LLM_MODEL,
        'messages': messages,
        'max_tokens': max_tokens,
        'temperature': temperature,
    }
    headers = {'Content-Type': 'application/json'}
    if settings.LLM_API_KEY:
        headers['Authorization'] = f'Bearer {settings.LLM_API_KEY}'

    url = settings.LLM_BASE_URL.rstrip('/') + '/chat/completions'
    request = urllib.request.Request(
        url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST'
    )

    try:
        with urllib.request.urlopen(request, timeout=DEFAULT_TIMEOUT) as response:
            data = json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as exc:
        body = ''
        try:
            body = exc.read().decode('utf-8', errors='replace')[:300]
        except Exception:
            pass
        raise AgentProviderError(
            f'Провайдер ИИ вернул ошибку HTTP {exc.code}. {body}'
        ) from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise AgentProviderError(
            f'Не удалось соединиться с ИИ-провайдером: {exc.reason}'
        ) from exc

    try:
        return data['choices'][0]['message']['content'].strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise AgentProviderError(
            'Провайдер ИИ вернул ответ в неожиданном формате.'
        ) from exc
