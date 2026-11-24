"""Формы приложения rooms (Темы 6, 11): аудитории и оборудование."""
from django import forms

from .models import Equipment, Room, RoomEquipment


class RoomForm(forms.ModelForm):
    """Форма создания/редактирования аудитории (администратор)."""

    equipment_rows = forms.ModelMultipleChoiceField(
        queryset=Equipment.objects.all(),
        required=False,
        label='Оборудование',
        widget=forms.CheckboxSelectMultiple,
        help_text='Отметьте оборудование, которое есть в аудитории.',
    )

    class Meta:
        model = Room
        fields = ('number', 'name', 'building', 'floor', 'capacity',
                  'room_type', 'status', 'description', 'photo', 'equipment_rows')
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}

    def clean_number(self):
        number = self.cleaned_data['number'].strip()
        qs = Room.objects.filter(number__iexact=number)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Аудитория с таким номером уже существует.')
        return number

    def clean_capacity(self):
        capacity = self.cleaned_data['capacity']
        if capacity < 1:
            raise forms.ValidationError('Вместимость должна быть не меньше 1.')
        return capacity


class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ('name', 'description')
        widgets = {'description': forms.Textarea(attrs={'rows': 2})}

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        qs = Equipment.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Оборудование с таким названием уже есть.')
        return name


class RoomEquipmentForm(forms.Form):
    """Задание количества для выбранного оборудования (модель RoomEquipment)."""
    quantity = forms.IntegerField(min_value=1, max_value=999, initial=1, label='Количество')
