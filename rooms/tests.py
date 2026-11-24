"""Тесты приложения rooms (Темы 5, 6, 9, 11)."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Equipment, Room, RoomEquipment

User = get_user_model()


def make_admin():
    return User.objects.create_user('admin', 'admin@mail.ru', 'Strong123pass', role='admin')


def make_room(number='101', capacity=20, status=Room.STATUS_ACTIVE, **kwargs):
    defaults = dict(name='Тестовая', building='1', floor=2, capacity=capacity)
    defaults.update(kwargs)
    return Room.objects.create(number=number, **defaults)


class RoomModelTest(TestCase):
    def test_str_and_available(self):
        room = make_room()
        self.assertEqual(str(room), '1-101 «Тестовая»')
        self.assertTrue(room.is_available())
        room.status = Room.STATUS_MAINTENANCE
        self.assertFalse(room.is_available())

    def test_unique_number(self):
        make_room('101')
        with self.assertRaises(Exception):
            make_room('101')

    def test_room_equipment_unique(self):
        room = make_room()
        eq = Equipment.objects.create(name='Проектор')
        RoomEquipment.objects.create(room=room, equipment=eq, quantity=2)
        link = RoomEquipment(room=room, equipment=eq, quantity=1)
        with self.assertRaises(Exception):
            link.save()

    def test_list_view(self):
        make_room('101')
        make_room('102')
        resp = self.client.get(reverse('rooms:list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '101')
        self.assertContains(resp, '102')

    def test_list_filter_capacity(self):
        make_room('101', capacity=5)
        make_room('102', capacity=50)
        resp = self.client.get(reverse('rooms:list') + '?min_capacity=30')
        self.assertContains(resp, '102')
        self.assertNotContains(resp, '101')

    def test_detail_view(self):
        room = make_room()
        resp = self.client.get(reverse('rooms:detail', room.pk))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Вместимость')


class RoomSearchTest(TestCase):
    def test_search_by_capacity(self):
        make_room('101', capacity=5)
        make_room('102', capacity=50)
        resp = self.client.get(reverse('rooms:search') + '?capacity=30')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '102')
        self.assertNotContains(resp, '101')

    def test_search_validation(self):
        resp = self.client.get(reverse('rooms:search') +
                               '?date=2030-01-01&time_start=12:00&time_end=10:00')
        self.assertContains(resp, 'позже')

    def test_search_excludes_busy_room(self):
        room = make_room()
        other = make_room('102')
        user = User.objects.create_user('u', 'u@mail.ru', 'Strong123pass')
        from datetime import date
        from bookings.models import Booking
        Booking.objects.create(user=user, room=room, date=date(2030, 1, 10),
                               time_start='10:00', time_end='12:00',
                               purpose='Пара', status=Booking.STATUS_CONFIRMED)
        url = reverse('rooms:search') + '?date=2030-01-10&time_start=11:00&time_end=13:00'
        resp = self.client.get(url)
        self.assertNotContains(resp, '1-101')
        self.assertContains(resp, '102')
        # Вне интервала обе свободны
        url2 = reverse('rooms:search') + '?date=2030-01-10&time_start=13:00&time_end=14:00'
        resp2 = self.client.get(url2)
        self.assertContains(resp2, '101')

    def test_search_excludes_maintenance(self):
        make_room('101', status=Room.STATUS_MAINTENANCE)
        make_room('102', status=Room.STATUS_ACTIVE)
        resp = self.client.get(reverse('rooms:search') + '?date=2030-01-10&time_start=10:00&time_end=12:00')
        self.assertNotContains(resp, '101')


class RoomAdminViewsTest(TestCase):
    def test_create_requires_admin(self):
        User.objects.create_user('u', 'u@mail.ru', 'Strong123pass')
        self.client.login(username='u', password='Strong123pass')
        resp = self.client.get(reverse('rooms:create'))
        self.assertIn(resp.status_code, (302, 403))

    def test_admin_create_room(self):
        admin = make_admin()
        self.client.login(username='admin', password='Strong123pass')
        resp = self.client.post(reverse('rooms:create'), {
            'number': '201', 'name': 'Новая', 'building': '2', 'floor': 1,
            'capacity': 15, 'room_type': 'computer', 'status': 'active',
            'description': 'Компьютеры',
        })
        self.assertRedirects(resp, reverse('rooms:detail', Room.objects.get(pk=1).pk))

    def test_admin_edit_room(self):
        make_admin()
        room = make_room()
        self.client.login(username='admin', password='Strong123pass')
        resp = self.client.post(reverse('rooms:edit', room.pk), {
            'number': '101', 'name': 'Обновлённая', 'building': '1', 'floor': 2,
            'capacity': 30, 'room_type': 'lecture', 'status': 'active',
        })
        room.refresh_from_db()
        self.assertEqual(room.name, 'Обновлённая')
        self.assertEqual(room.capacity, 30)

    def test_admin_delete_room(self):
        make_admin()
        room = make_room()
        self.client.login(username='admin', password='Strong123pass')
        resp = self.client.post(reverse('rooms:delete', room.pk))
        self.assertRedirects(resp, reverse('rooms:list'))
        self.assertFalse(Room.objects.filter(pk=room.pk).exists())


class EquipmentViewsTest(TestCase):
    def test_admin_crud(self):
        make_admin()
        self.client.login(username='admin', password='Strong123pass')
        resp = self.client.post(reverse('rooms:equipment_create'),
                                {'name': 'Проектор', 'description': ''})
        self.assertEqual(Equipment.objects.count(), 1)
        eq = Equipment.objects.first()
        resp = self.client.post(reverse('rooms:equipment_edit', eq.pk),
                                {'name': 'Проектор Epson'})
        eq.refresh_from_db()
        self.assertEqual(eq.name, 'Проектор Epson')
        resp = self.client.post(reverse('rooms:equipment_delete', eq.pk))
        self.assertEqual(Equipment.objects.count(), 0)
