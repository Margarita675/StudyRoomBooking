"""Тесты бронирования (Темы 8, 9, 10): конфликты, права, статусы."""
from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import Booking
from rooms.models import Room

User = get_user_model()


def make_room(number='101'):
    return Room.objects.create(number=number, name='Тест', building='1', floor=1, capacity=10)


def make_user(username='student', email='student@mail.ru', role='user'):
    return User.objects.create_user(username, email, 'Strong123pass', role=role)


def make_booking(user, room, d=date(2030, 3, 1), s='10:00', e='12:00',
                 status=Booking.STATUS_CONFIRMED):
    return Booking.objects.create(user=user, room=room, date=d, time_start=s,
                                  time_end=e, purpose='Пара', status=status)


class ConflictTest(TestCase):
    def setUp(self):
        self.user = make_user()
        self.room = make_room()

    def test_confirmed_blocks_overlapping(self):
        make_booking(self.user, self.room)
        b = Booking(user=self.user, room=self.room, date=date(2030, 3, 1),
                    time_start='11:00', time_end='13:00', purpose='x')
        with self.assertRaises(ValidationError):
            b.save()

    def test_partial_overlap_start_inside(self):
        make_booking(self.user, self.room, s='10:00', e='12:00')
        b = Booking(user=self.user, room=self.room, date=date(2030, 3, 1),
                    time_start='09:00', time_end='10:30', purpose='x')
        with self.assertRaises(ValidationError):
            b.save()

    def test_nested_interval_blocked(self):
        make_booking(self.user, self.room, s='10:00', e='14:00')
        b = Booking(user=self.user, room=self.room, date=date(2030, 3, 1),
                    time_start='11:00', time_end='12:00', purpose='x')
        with self.assertRaises(ValidationError):
            b.save()

    def test_adjacent_slots_allowed(self):
        make_booking(self.user, self.room, s='10:00', e='12:00')
        b = Booking(user=self.user, room=self.room, date=date(2030, 3, 1),
                    time_start='12:00', time_end='14:00', purpose='x')
        b.save()  # границы не пересекаются
        self.assertEqual(Booking.objects.count(), 2)

    def test_time_end_before_start(self):
        b = Booking(user=self.user, room=self.room, date=date(2030, 3, 1),
                    time_start='12:00', time_end='10:00', purpose='x')
        with self.assertRaises(ValidationError):
            b.save()

    def test_past_date_rejected(self):
        b = Booking(user=self.user, room=self.room, date=date(2020, 1, 1),
                    time_start='10:00', time_end='11:00', purpose='x')
        with self.assertRaises(ValidationError):
            b.save()

    def test_same_slot_blocked(self):
        make_booking(self.user, self.room)
        b = Booking(user=self.user, room=self.room, date=date(2030, 3, 1),
                    time_start='10:00', time_end='12:00', purpose='x')
        with self.assertRaises(ValidationError):
            b.save()

    def test_pending_also_blocks(self):
        make_booking(self.user, self.room, status=Booking.STATUS_PENDING)
        b = Booking(user=self.user, room=self.room, date=date(2030, 3, 1),
                    time_start='10:30', time_end='11:30', purpose='x')
        with self.assertRaises(ValidationError):
            b.save()


class BookingFlowTest(TestCase):
    def setUp(self):
        self.user = make_user()
        self.room = make_room()

    def test_create_booking_via_form(self):
        self.client.login(username='student', password='Strong123pass')
        resp = self.client.post(reverse('bookings:create', self.room.pk), {
            'room': self.room.pk, 'date': '2030-03-01', 'time_start': '10:00',
            'time_end': '12:00', 'purpose': 'Учебная встреча',
        }, follow=True)
        self.assertEqual(Booking.objects.count(), 1)
        b = Booking.objects.first()
        self.assertEqual(b.status, Booking.STATUS_PENDING)

    def test_conflict_shows_error(self):
        make_booking(self.user, self.room)
        self.client.login(username='student', password='Strong123pass')
        resp = self.client.post(reverse('bookings:create', self.room.pk), {
            'room': self.room.pk, 'date': '2030-03-01', 'time_start': '11:00',
            'time_end': '13:00', 'purpose': 'Конфликт',
        })
        self.assertEqual(Booking.objects.count(), 1)
        self.assertContains(resp, 'занята')

    def test_my_bookings_only_own(self):
        other = make_user('other', 'other@mail.ru')
        mine = make_booking(self.user, self.room, purpose='Моя')
        foreign = make_booking(other, self.room, s='14:00', e='16:00', purpose='Чужая')
        self.client.login(username='student', password='Strong123pass')
        resp = self.client.get(reverse('bookings:my'))
        self.assertContains(resp, 'Моя')
        self.assertNotContains(resp, 'Чужая')

    def test_cannot_cancel_foreign_booking(self):
        other = make_user('other', 'other@mail.ru')
        foreign = make_booking(other, self.room)
        self.client.login(username='student', password='Strong123pass')
        resp = self.client.post(reverse('bookings:cancel', foreign.pk))
        foreign.refresh_from_db()
        self.assertEqual(foreign.status, Booking.STATUS_CONFIRMED)

    def test_cancel_own_booking(self):
        b = make_booking(self.user, self.room, status=Booking.STATUS_PENDING)
        self.client.login(username='student', password='Strong123pass')
        self.client.post(reverse('bookings:cancel', b.pk))
        b.refresh_from_db()
        self.assertEqual(b.status, Booking.STATUS_CANCELLED)

    def test_cancelled_slot_freed(self):
        b = make_booking(self.user, self.room)
        b.status = Booking.STATUS_CANCELLED
        b.save(update_fields=['status'])
        new_b = Booking(user=self.user, room=self.room, date=date(2030, 3, 1),
                        time_start='10:00', time_end='12:00', purpose='Новьё')
        new_b.save()  # отменённая бронь не мешает
        self.assertEqual(Booking.objects.count(), 2)


class AdminBookingTest(TestCase):
    def setUp(self):
        self.admin = make_user('admin', 'admin@mail.ru', role='admin')
        self.user = make_user()
        self.room = make_room()
        self.client.login(username='admin', password='Strong123pass')

    def test_admin_confirm(self):
        b = make_booking(self.user, self.room, status=Booking.STATUS_PENDING)
        resp = self.client.post(reverse('bookings:admin'), {
            'booking_id': b.pk, 'action': 'confirm'})
        b.refresh_from_db()
        self.assertEqual(b.status, Booking.STATUS_CONFIRMED)

    def test_admin_reject(self):
        b = make_booking(self.user, self.room, status=Booking.STATUS_PENDING)
        self.client.post(reverse('bookings:admin'), {
            'booking_id': b.pk, 'action': 'reject'})
        b.refresh_from_db()
        self.assertEqual(b.status, Booking.STATUS_REJECTED)

    def test_admin_cannot_confirm_conflict(self):
        b1 = make_booking(self.user, self.room, status=Booking.STATUS_PENDING)
        make_booking(self.admin, self.room, status=Booking.STATUS_CONFIRMED)
        self.client.post(reverse('bookings:admin'), {
            'booking_id': b1.pk, 'action': 'confirm'})
        b1.refresh_from_db()
        self.assertEqual(b1.status, Booking.STATUS_PENDING)

    def test_admin_views_restricted(self):
        self.client.logout()
        make_user()
        self.client.login(username='student', password='Strong123pass')
        resp = self.client.get(reverse('bookings:admin'))
        self.assertIn(resp.status_code, (302, 403))

    def test_room_schedule(self):
        make_booking(self.user, self.room)
        resp = self.client.get(reverse('bookings:room_schedule', self.room.pk))
        self.assertContains(resp, '1-101')

    def test_public_schedule_filter(self):
        make_booking(self.user, self.room)
        resp = self.client.get(reverse('bookings:schedule') + '?date=2030-03-01')
        self.assertContains(resp, '1-101')
        resp = self.client.get(reverse('bookings:schedule') + '?date=2030-03-02')
        self.assertNotContains(resp, '1-101')
