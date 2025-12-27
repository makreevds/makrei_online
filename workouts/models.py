from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.contrib.auth.models import User


class WeightEntry(models.Model):
    """
    Модель записи веса на конкретную дату.
    Используется для отслеживания изменения веса тела на графике.
    Привязана к пользователю.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='weight_entries',
        verbose_name='Пользователь',
        help_text='Владелец записи веса'
    )
    date = models.DateField(
        default=timezone.now,
        verbose_name='Дата',
        help_text='Дата измерения веса'
    )
    weight_kg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Вес (кг)',
        help_text='Вес тела в килограммах'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Заметки',
        help_text='Дополнительные заметки (например, время измерения, условия)'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создано'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Обновлено'
    )
    
    class Meta:
        verbose_name = 'Запись веса'
        verbose_name_plural = 'Записи веса'
        ordering = ['-date', '-created_at']
        unique_together = ['user', 'date']  # Один вес на дату для каждого пользователя
    
    def __str__(self):
        return f'{self.user.username} - {self.date} - {self.weight_kg} кг'


class Workout(models.Model):
    """
    Модель проведенной тренировки.
    Привязана к пользователю.
    """
    WORKOUT_TYPES = [
        ('strength', 'Силовая'),
        ('endurance', 'Выносливость'),
        ('cardio', 'Кардио'),
        ('flexibility', 'Гибкость'),
        ('mixed', 'Смешанная'),
        ('yoga', 'Йога'),
        ('pilates', 'Пилатес'),
        ('other', 'Другое'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='workouts',
        verbose_name='Пользователь',
        help_text='Владелец тренировки'
    )
    date = models.DateField(
        default=timezone.now,
        verbose_name='Дата',
        help_text='Дата проведения тренировки'
    )
    workout_type = models.CharField(
        max_length=20,
        choices=WORKOUT_TYPES,
        default='mixed',
        verbose_name='Тип тренировки',
        help_text='Тип тренировки: силовая, выносливость, кардио и т.д.'
    )
    duration_minutes = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        verbose_name='Продолжительность (минуты)',
        help_text='Продолжительность тренировки в минутах'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Заметки',
        help_text='Дополнительные заметки о тренировке'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создано'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Обновлено'
    )
    
    class Meta:
        verbose_name = 'Тренировка'
        verbose_name_plural = 'Тренировки'
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.get_workout_type_display()} - {self.date}'
