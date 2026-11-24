"""Тесты REST API (Тема 12): JWT, коды 200/201/204/400/401/403/404/422."""
from datetime import date, time

from rest_framework.test import APIClient, APITestCase

from bookings.models import Booking
from rooms.models import Equipment, Room


def make_room(number='101', capacity=10):
    return Room.objects.create(number=number, name='API', building='1', floor=1,
                               capacity=capacity)


class AuthApiTest(APITestCase):
    def test_register_201(self):
        resp = self.client.post('/api/auth/register/', {
            'username': 'api_user', 'email': 'api@mail.ru',
            'password': 'Strong123pass'})
        self.assertEqual(resp.status_code, 201)

    def test_register_weak_password_422(self):
        resp = self.client.post('/api/auth/register/', {
            'username': 'weak', 'email': 'w@mail.ru', 'password': '123'})
        self.assertEqual(resp.status_code, 422)

    def test_login_200_and_wrong_401(self):
        self.client.post('/api/auth/register/', {
            'username': 'api_user', 'email': 'api@mail.ru',
            'password': 'Strong123pass'})
        resp = self.client.post('/api/auth/login/', {
            'username': 'api_user', 'password': 'Strong123pass'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn('access', resp.data)
        resp = self.client.post('/api/auth/login/', {
            'username': 'api_user', 'password': 'wrong'})
        self.assertEqual(resp.status_code, 401)


class RoomApiTest(APITestCase):
    def setUp(self):
        self.room = make_room()
        self.admin_token = self._token('admin', 'a@mail.ru', 'Strong123pass', role='admin')
        self.user_token = self._token('user', 'u@mail.ru', 'Strong123pass')

    def _token(self, username, email, password, role=None):
        from accounts.models import User
        User.objects.create_user(username, email, password, role=role or 'user')
        resp = self.client.post('/api/auth/login/', {'username': username,
                                                     'password': password})
        return resp.data['access']

    def _auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_rooms_list_public(self):
        resp = self.client.get('/api/rooms/')
        self.assertEqual(resp.status_code, 200)

    def test_create_room_admin_only(self):
        self._auth(self.user_token)
        resp = self.client.post('/api/rooms/', {'number': '999', 'name': 'X',
                                                'building': '1', 'floor': 1,
                                                'capacity': 5})
        self.assertEqual(resp.status_code, 403)
        self._auth(self.admin_token)
        resp = self.client.post('/api/rooms/', {'number': '999', 'name': 'X',
                                                'building': '1', 'floor': 1,
                                                'capacity': 5})
        self.assertEqual(resp.status_code, 201)

    def test_delete_room_admin_only(self):
        self._auth(self.admin_token)
        resp = self.client.delete(f'/api/rooms/{self.room.pk}/')
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(Room.objects.filter(pk=self.room.pk).exists())

    def test_room_404(self):
        self._auth(self.admin_token)
        resp = self.client.delete('/api/rooms/99999/')
        self.assertEqual(resp.status_code, 404)


class BookingApiTest(APITestCase):
    def setUp(self):
        self.room = make_room()
        self.user_token = self._token('user', 'u@mail.ru', 'Strong123pass')
        self.admin_token = self._token('admin', 'a@mail.ru', 'Strong123pass', role='admin')

    def _token(self, username, email, password, role=None):
        from accounts.models import User
        User.objects.create_user(username, email, password, role=role or 'user')
        resp = self.client.post('/api/auth/login/', {'username': username,
                                                     'password': password})
        return resp.data['access']

    def _auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def _payload(self, s='10:00', e='12:00'):
        return {'room': self.room.pk, 'date': '2030-04-01',
                'time_start': s, 'time_end': e, 'purpose': 'API бронь'}

    def test_create_booking_201(self):
        self._auth(self.user_token)
        resp = self.client.post('/api/bookings/', self._payload())
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data['status'], 'pending')

    def test_requires_auth_401(self):
        resp = self.client.post('/api/bookings/', self._payload())
        self.assertEqual(resp.status_code, 401)

    def test_overlap_422(self):
        self._auth(self.user_token)
        self.client.post('/api/bookings/', self._payload())
        resp = self.client.post('/api/bookings/', self._payload(s='11:00', e='13:00'))
        self.assertEqual(resp.status_code, 422)

    def test_time_order_422(self):
        self._auth(self.user_token)
        resp = self.client.post('/api/bookings/', self._payload(s='12:00', e='10:00'))
        self.assertEqual(resp.status_code, 422)

    def test_idor_403(self):
        self._auth(self.user_token)
        resp = self.client.post('/api/bookings/', self._payload())
        booking_id = resp.data['id']
        other_token = self._token('other', 'o@mail.ru', 'Strong123pass')
        self._auth(other_token)
        resp = self.client.get(f'/api/bookings/{booking_id}/')
        self.assertEqual(resp.status_code, 403)

    def test_cancel_204(self):
        self._auth(self.user_token)
        resp = self.client.post('/api/bookings/', self._payload())
        booking_id = resp.data['id']
        resp = self.client.delete(f'/api/bookings/{booking_id}/')
        self.assertEqual(resp.status_code, 204)

    def test_admin_confirm_patch(self):
        self._auth(self.user_token)
        resp = self.client.post('/api/bookings/', self._payload())
        booking_id = resp.data['id']
        self._auth(self.admin_token)
        resp = self.client.patch(f'/api/bookings/{booking_id}/', {'status': 'confirmed'})
        self.assertEqual(resp.status_code, 200)

    def test_list_only_own(self):
        self._auth(self.user_token)
        self.client.post('/api/bookings/', self._payload())
        other_token = self._token('other', 'o@mail.ru', 'Strong123pass')
        self._auth(other_token)
        resp = self.client.get('/api/bookings/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 0)


class SearchApiTest(APITestCase):
    def setUp(self):
        self.room = make_room('201')
        self.other = make_room('202', capacity=50)

    def test_search_filters_and_free(self):
        resp = self.client.get('/api/rooms/search/?date=2030-05-01&time_start=10:00&time_end=12:00&capacity=30')
        self.assertEqual(resp.status_code, 200)
        numbers = [r['number'] for r in resp.data['results']]
        self.assertEqual(numbers, ['202'])

    def test_search_excludes_busy(self):
        from accounts.models import User
        user = User.objects.create_user('u', 'u@mail.ru', 'Strong123pass')
        Booking.objects.create(user=user, room=self.other, date=date(2030, 5, 1),
                               time_start=time(10, 0), time_end=time(12, 0),
                               purpose='x')
        resp = self.client.get('/api/rooms/search/?date=2030-05-01&time_start=11:00&time_end=13:00')
        self.assertEqual(resp.data['results'], [])

    def test_missing_params_400(self):
        resp = self.client.get('/api/rooms/search/')
        self.assertEqual(resp.status_code, 400)

    def test_schedule_endpoint(self):
        resp = self.client.get(f'/api/rooms/{self.other.pk}/schedule/?date=2030-05-01')
        self.assertEqual(resp.status_code, 200)


class ServiceRoutesTest(APITestCase):
    def test_ping_and_health(self):
        self.assertEqual(self.client.get('/api/ping/').status_code, 200)
        self.assertEqual(self.client.get('/health/').status_code, 200)
