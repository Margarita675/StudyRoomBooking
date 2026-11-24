from django.contrib import admin

from .models import Equipment, Room, RoomEquipment


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class RoomEquipmentInline(admin.TabularInline):
    model = RoomEquipment
    extra = 1


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'building', 'floor', 'capacity',
                    'room_type', 'status')
    list_filter = ('building', 'room_type', 'status')
    search_fields = ('number', 'name')
    inlines = (RoomEquipmentInline,)
