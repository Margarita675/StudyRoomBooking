/* Клиентская часть ИИ-агента (Тема 14, раздел 6).
   Браузер обращается ТОЛЬКО к нашему серверу (POST /agent/send/),
   ключ ИИ-провайдера браузеру недоступен. */
(function () {
    'use strict';

    var chat = document.getElementById('agent-chat');
    if (!chat) return;

    var form = document.getElementById('agent-form');
    var input = document.getElementById('agent-input');
    var btn = document.getElementById('agent-send-btn');
    var list = document.getElementById('agent-messages');
    var sendUrl = chat.getAttribute('data-send-url');

    function addMessage(role, text) {
        var div = document.createElement('div');
        div.className = 'agent-msg ' + role;
        var who = document.createElement('span');
        who.className = 'agent-who';
        who.textContent = (role === 'user' ? 'Вы' : 'Помощник') + ':';
        var body = document.createElement('span');
        body.className = 'agent-text';
        body.textContent = text; // textContent — защита от XSS
        div.appendChild(who);
        div.appendChild(body);
        list.appendChild(div);
        list.scrollTop = list.scrollHeight;
    }

    form.addEventListener('submit', function (event) {
        event.preventDefault();
        var text = input.value.trim();
        if (!text) return;

        var csrf = form.querySelector('[name=csrfmiddlewaretoken]').value;
        addMessage('user', text);
        input.value = '';
        btn.disabled = true;
        addMessage('assistant', '…думаю');

        fetch(sendUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf
            },
            credentials: 'same-origin',
            body: JSON.stringify({ message: text })
        })
            .then(function (response) {
                return response.json().then(function (data) {
                    return { status: response.status, data: data };
                });
            })
            .then(function (result) {
                // убрать «…думаю»
                var last = list.lastElementChild;
                if (last && last.textContent.indexOf('…думаю') !== -1) {
                    list.removeChild(last);
                }
                if (result.data.ok) {
                    addMessage('assistant', result.data.answer);
                } else {
                    addMessage('assistant', 'Ошибка: ' + (result.data.error || 'попробуйте позже.'));
                }
            })
            .catch(function () {
                var last = list.lastElementChild;
                if (last && last.textContent.indexOf('…думаю') !== -1) {
                    list.removeChild(last);
                }
                addMessage('assistant', 'Сервер недоступен. Проверьте, что запущен python manage.py runserver.');
            })
            .finally(function () {
                btn.disabled = false;
                input.focus();
            });
    });
})();
