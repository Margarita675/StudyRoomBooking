"""Маршруты ИИ-агента (Тема 14)."""
from django.urls import path

from . import views

app_name = 'agent'

urlpatterns = [
    path('agent/', views.chat_view, name='chat'),
    path('agent/send/', views.send_view, name='send'),
    path('agent/clear/', views.clear_view, name='clear'),
]
