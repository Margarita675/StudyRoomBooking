from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('room', 'user', 'date', 'time_start', 'time_end',
                    'purpose', 'status', 'created_at')
    list_filter = ('status', 'room')
    search_fields = ('user__username', 'purpose')
