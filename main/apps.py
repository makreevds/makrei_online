"""Конфигурация приложения main."""
from django.apps import AppConfig


class MainConfig(AppConfig):
    """Конфигурация приложения main."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'
    verbose_name = 'Основное приложение'

