"""Корневые маршруты проекта StudyRoomBooking."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from accounts.views import home_view
from api.views import health

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health, name='health'),
    path('api/', include('api.urls')),
    path('bookings/', include('bookings.urls')),
    path('rooms/', include('rooms.urls')),
    path('', home_view, name='home'),
    path('', include('accounts.urls')),
    path('', include('agent.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
