"""Модели для приложения main."""
from typing import Optional
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class TelegramProfile(models.Model):
    """
    Профиль пользователя, связанный с Telegram аккаунтом.
    
    Хранит данные пользователя из Telegram Login Widget:
    - telegram_id: уникальный идентификатор пользователя в Telegram
    - username: имя пользователя в Telegram (может быть None)
    - first_name: имя пользователя
    - last_name: фамилия пользователя (может быть None)
    - photo_url: URL аватара пользователя (может быть None)
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='telegram_profile',
        verbose_name='Пользователь'
    )
    telegram_id = models.BigIntegerField(
        unique=True,
        verbose_name='Telegram ID',
        help_text='Уникальный идентификатор пользователя в Telegram'
    )
    username = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Telegram Username',
        help_text='Имя пользователя в Telegram (@username)'
    )
    first_name = models.CharField(
        max_length=255,
        verbose_name='Имя',
        help_text='Имя пользователя из Telegram'
    )
    last_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Фамилия',
        help_text='Фамилия пользователя из Telegram'
    )
    photo_url = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name='URL фото',
        help_text='URL аватара пользователя в Telegram'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    
    class Meta:
        verbose_name = 'Telegram профиль'
        verbose_name_plural = 'Telegram профили'
        db_table = 'telegram_profiles'
        indexes = [
            models.Index(fields=['telegram_id']),
            models.Index(fields=['username']),
        ]
    
    def __str__(self) -> str:
        """Возвращает строковое представление профиля."""
        return f"{self.user.username} (Telegram: {self.telegram_id})"
    
    def get_full_name(self) -> str:
        """Возвращает полное имя пользователя."""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

