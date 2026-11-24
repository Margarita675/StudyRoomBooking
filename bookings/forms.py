"""Форма бронирования (Тема 8) с серверной валидацией."""
import datetime as dt

from django import forms
from django.utils import timezone

from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ('room', 'date', 'time_start', 'time_end', 'purpose', 'comment')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time_start': forms.TimeInput(attrs={'type': 'time'}),
            'time_end': forms.TimeInput(attrs={'type': 'time'}),
            'comment': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['room'].widget = forms.HiddenInput()

    def clean_date(self):
        date = self.cleaned_data['date']
        if date < timezone.localdate():
            raise forms.ValidationError('Нельзя бронировать на прошедшую дату.')
        return date

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('time_start')
        end = cleaned.get('time_end')
        if start and end and start >= end:
            self.add_error('time_end', 'Время окончания должно быть позже времени начала.')
        return cleaned
