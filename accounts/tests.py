"""
Тесты регистрации, входа и RBAC (Темы 6, 8).
Запуск: python manage.py test accounts
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AuthFlowTests(TestCase):
    def test_register_creates_user_with_role_user(self):
        resp = self.client.post(reverse('accounts:register'), {
            'username': 'vasya', 'email': 'vasya@mail.ru',
            'password1': 'StrongPass123', 'password2': 'StrongPass123',
        })
        user = User.objects.get(username='vasya')
        self.assertEqual(user.role, User.ROLE_USER)
        self.assertEqual(user.email, 'vasya@mail.ru')
        self.assertNotEqual(user.password, 'StrongPass123')  # пароль хеширован

    def test_register_duplicate_email_rejected(self):
        User.objects.create_user('a', 'dup@mail.ru', 'StrongPass123')
        resp = self.client.post(reverse('accounts:register'), {
            'username': 'b', 'email': 'dup@mail.ru',
            'password1': 'StrongPass123', 'password2': 'StrongPass123',
        })
        self.assertEqual(User.objects.filter(email='dup@mail.ru').count(), 1)
        self.assertEqual(resp.status_code, 200)

    def test_login_logout(self):
        User.objects.create_user('vasya', 'vasya@mail.ru', 'StrongPass123')
        self.assertTrue(self.client.login(username='vasya', password='StrongPass123'))
        resp = self.client.get(reverse('rooms:list'))
        self.assertEqual(resp.status_code, 200)
        self.client.logout()
        resp = self.client.get(reverse('rooms:list'))
        self.assertEqual(resp.status_code, 302)  # редирект на login

    def test_profile_requires_auth(self):
        resp = self.client.get(reverse('accounts:profile'))
        self.assertEqual(resp.status_code, 302)


class RbacTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user('admin', 'a@e.com', 'AdminPass123', role='admin')
        self.user = User.objects.create_user('user', 'u@e.com', 'UserPass123')

    def test_admin_dashboard_forbidden_for_user(self):
        self.client.login(username='user', password='UserPass123')
        resp = self.client.get(reverse('accounts:admin_dashboard'))
        self.assertEqual(resp.status_code, 403)

    def test_admin_dashboard_ok_for_admin(self):
        self.client.login(username='admin', password='AdminPass123')
        resp = self.client.get(reverse('accounts:admin_dashboard'))
        self.assertEqual(resp.status_code, 200)

    def test_block_user(self):
        self.client.login(username='admin', password='AdminPass123')
        self.client.post(reverse('accounts:admin_block_user', args=[self.user.pk]))
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)


class PasswordResetTests(TestCase):
    """Тема 7: токены одноразовые, в БД хранится только хеш."""

    def setUp(self):
        self.user = User.objects.create_user('vasya', 'vasya@mail.ru', 'OldPass123')

    def _request_token(self):
        self.client.post(reverse('accounts:forgot_password'), {'email': 'vasya@mail.ru'})
        token = PasswordResetToken.objects.filter(user=self.user, is_used=False).first()
        # восстановим исходный токен по хешу невозможно — поэтому запросим новый
        return token

    def test_token_hash_stored_not_raw(self):
        import secrets
        from accounts.models import PasswordResetToken
        raw = secrets.token_urlsafe(32)
        t = PasswordResetToken.objects.create(user=self.user, token_hash=PasswordResetToken.hash_token(raw))
        self.assertNotEqual(t.token_hash, raw)
        self.assertEqual(len(t.token_hash), 64)
        self.assertTrue(t.is_valid())

    def test_reset_page_invalid_token_redirects(self):
        resp = self.client.get(reverse('accounts:reset_password', args=['fake-token-value']))
        self.assertEqual(resp.status_code, 302)  # редирект на login с ошибкой
