"""Административный интерфейс для приложения main."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import TelegramProfile


@admin.register(TelegramProfile)
class TelegramProfileAdmin(admin.ModelAdmin):
    """Административный интерфейс для модели TelegramProfile."""
    
    list_display = ('user', 'telegram_id', 'username', 'first_name', 'last_name', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'telegram_id', 'username', 'first_name', 'last_name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Пользователь', {
            'fields': ('user',)
        }),
        ('Telegram данные', {
            'fields': ('telegram_id', 'username', 'first_name', 'last_name', 'photo_url')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

