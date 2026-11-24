from django.urls import path

from . import views

app_name = 'bookings'

urlpatterns = [
    path('my/', views.my_bookings_view, name='my'),
    path('schedule/', views.schedule_view, name='schedule'),
    path('<int:booking_id>/', views.booking_detail_view, name='detail'),
    path('<int:booking_id>/cancel/', views.booking_cancel_view, name='cancel'),
    path('room/<int:room_id>/', views.booking_create_view, name='create'),
    path('admin/', views.admin_bookings_view, name='admin'),
    path('admin/room/<int:room_id>/', views.admin_schedule_view, name='room_schedule'),
]
