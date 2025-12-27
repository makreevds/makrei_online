"""
Формы для работы с данными пользователя.
"""
from django import forms
from .models import WeightEntry, Workout


class WeightEntryForm(forms.ModelForm):
    """
    Форма для добавления/редактирования записи веса.
    """
    class Meta:
        model = WeightEntry
        fields = ['date', 'weight_kg', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input',
                'required': True
            }),
            'weight_kg': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'min': '0',
                'required': True,
                'placeholder': 'Введите вес в кг'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Дополнительные заметки (необязательно)'
            }),
        }
        labels = {
            'date': 'Дата',
            'weight_kg': 'Вес (кг)',
            'notes': 'Заметки',
        }


class WorkoutForm(forms.ModelForm):
    """
    Форма для добавления/редактирования тренировки.
    """
    class Meta:
        model = Workout
        fields = ['date', 'workout_type', 'duration_minutes', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input',
                'required': True
            }),
            'workout_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': '1',
                'placeholder': 'Продолжительность в минутах (необязательно)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Дополнительные заметки (необязательно)'
            }),
        }
        labels = {
            'date': 'Дата',
            'workout_type': 'Тип тренировки',
            'duration_minutes': 'Продолжительность (минуты)',
            'notes': 'Заметки',
        }

