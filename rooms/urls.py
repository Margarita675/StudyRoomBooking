from django.urls import path

from . import views

app_name = 'rooms'

urlpatterns = [
    path('', views.room_list_view, name='list'),
    path('search/', views.room_search_view, name='search'),
    path('equipment/', views.equipment_list_view, name='equipment'),
    path('equipment/new/', views.equipment_create_view, name='equipment_create'),
    path('equipment/<int:equipment_id>/edit/', views.equipment_edit_view, name='equipment_edit'),
    path('equipment/<int:equipment_id>/delete/', views.equipment_delete_view, name='equipment_delete'),
    path('new/', views.room_create_view, name='create'),
    path('<int:room_id>/', views.room_detail_view, name='detail'),
    path('<int:room_id>/edit/', views.room_edit_view, name='edit'),
    path('<int:room_id>/delete/', views.room_delete_view, name='delete'),
]
