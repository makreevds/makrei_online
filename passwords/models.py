"""Модели для хранения зашифрованных паролей."""
from typing import Optional
from django.db import models
from django.core.validators import EmailValidator
from django.utils import timezone


class PasswordEntry(models.Model):
    """
    Модель для хранения зашифрованных паролей от различных сервисов.
    
    Пароли хранятся в зашифрованном виде и могут быть расшифрованы
    только с помощью мастер-пароля.
    """
    
    service = models.CharField(
        max_length=200,
        verbose_name='Сервис',
        help_text='Название сайта или сервиса'
    )
    login = models.CharField(
        max_length=200,
        verbose_name='Логин',
        help_text='Имя пользователя или email для входа'
    )
    password_encrypted = models.TextField(
        verbose_name='Пароль (зашифрован)',
        help_text='Пароль в зашифрованном виде'
    )
    email = models.EmailField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Email',
        help_text='Email адрес (необязательно)',
        validators=[EmailValidator()]
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
        verbose_name = 'Пароль'
        verbose_name_plural = 'Пароли'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['service']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self) -> str:
        """Строковое представление записи."""
        return f"{self.service} - {self.login}"
