from django.urls import path

from . import views

urlpatterns = [
    # Служебные (Тема 5)
    path('ping/', views.ping, name='api_ping'),
    # Аутентификация (Тема 12)
    path('auth/register/', views.RegisterAPIView.as_view(), name='api_register'),
    path('auth/login/', views.LoginAPIView.as_view(), name='api_login'),
    path('auth/password-reset/request/', views.PasswordResetRequestAPIView.as_view(),
         name='api_password_reset_request'),
    path('auth/password-reset/confirm/', views.PasswordResetConfirmAPIView.as_view(),
         name='api_password_reset_confirm'),
    # Аудитории
    path('rooms/', views.RoomListAPIView.as_view(), name='api_rooms'),
    path('rooms/<int:room_id>/', views.RoomDetailAPIView.as_view(), name='api_room_detail'),
    path('rooms/search/', views.RoomSearchAPIView.as_view(), name='api_room_search'),
    path('rooms/<int:room_id>/schedule/', views.RoomScheduleAPIView.as_view(),
         name='api_room_schedule'),
    # Оборудование
    path('equipment/', views.EquipmentListAPIView.as_view(), name='api_equipment'),
    # Бронирования
    path('bookings/', views.BookingListAPIView.as_view(), name='api_bookings'),
    path('bookings/<int:booking_id>/', views.BookingDetailAPIView.as_view(),
         name='api_booking_detail'),
]
