"""Тесты ИИ-агента (Тема 14): доступ, валидация, сохранение истории, права."""
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from agent.models import AiMessage


class AgentAccessTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='st', email='st@ex.ru', password='Passw0rd123')
        self.client.login(username='st', password='Passw0rd123')
        self.page_url = reverse('agent:chat')
        self.send_url = reverse('agent:send')

    def test_page_requires_login(self):
        self.client.logout()
        response = self.client.get(self.page_url)
        self.assertEqual(response.status_code, 302)  # redirect на /login/

    def test_page_ok_for_logged_in(self):
        response = self.client.get(self.page_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ИИ-помощник')

    def test_send_requires_post(self):
        response = self.client.get(self.send_url)
        self.assertEqual(response.status_code, 405)

    def test_send_without_csrf_rejected(self):
        self.client.environ_defaults = {}
        response = self.client.post(
            self.send_url,
            data='{"message": "привет"}',
            content_type='application/json',
            **{'HTTP_X_CSRFTOKEN': 'wrong-token'},
        )
        self.assertEqual(response.status_code, 403)  # CSRF-защита (Тема 15)

    def test_send_empty_message_400(self):
        response = self.client.post(
            self.send_url, data='{"message": "  "}',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_send_too_long_message_400(self):
        long_text = 'а' * 2001
        response = self.client.post(
            self.send_url, data=f'{{"message": "{long_text}"}}',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_user_message_saved_before_llm_call(self):
        """Реплика пользователя сохраняется в БД даже при недоступном провайдере."""
        self.client.post(
            self.send_url, data='{"message": "как забронировать?"}',
            content_type='application/json',
        )
        self.assertTrue(
            AiMessage.objects.filter(user=self.user, role=AiMessage.ROLE_USER).exists()
        )


class AgentModelTests(TestCase):
    def test_history_ordering_and_limit(self):
        user = User.objects.create_user(username='h', email='h@ex.ru', password='Passw0rd123')
        for i in range(25):
            AiMessage.objects.create(user=user, role=AiMessage.ROLE_USER, content=f'msg {i}')
        history = AiMessage.history_for(user, limit=20)
        self.assertEqual(len(history), 20)
        self.assertEqual(history[-1]['content'], 'msg 24')  # хронологический порядок
