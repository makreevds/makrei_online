"""Административный интерфейс для приложения main."""
from typing import Optional
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import TelegramProfile


class TelegramProfileInline(admin.StackedInline):
    """
    Inline-администратор для отображения Telegram профиля внутри пользователя.
    
    Позволяет редактировать данные Telegram непосредственно в форме пользователя.
    """
    model = TelegramProfile
    can_delete = False
    verbose_name = 'Telegram профиль'
    verbose_name_plural = 'Telegram данные'
    fieldsets = (
        ('Telegram данные', {
            'fields': ('telegram_id', 'username', 'first_name', 'last_name', 'photo_url'),
            'description': 'Данные пользователя из Telegram Login Widget'
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    extra = 0
    max_num = 1


class CustomUserAdmin(BaseUserAdmin):
    """
    Расширенный администратор пользователей с поддержкой Telegram профиля.
    
    Включает inline для отображения и редактирования Telegram данных
    непосредственно в форме пользователя.
    """
    inlines = (TelegramProfileInline,)
    
    def get_inline_instances(self, request, obj: Optional[User] = None):
        """Возвращает inline-экземпляры для формы пользователя."""
        return super().get_inline_instances(request, obj)


# Перерегистрируем UserAdmin с нашими изменениями
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# Оставляем отдельную регистрацию для удобства поиска, но основное редактирование в User
@admin.register(TelegramProfile)
class TelegramProfileAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для модели TelegramProfile.
    
    Используется для поиска и просмотра профилей, но основное редактирование
    рекомендуется выполнять через форму пользователя.
    """
    
    list_display = ('user', 'telegram_id', 'username', 'first_name', 'last_name', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'telegram_id', 'username', 'first_name', 'last_name')
    readonly_fields = ('created_at', 'updated_at', 'user')
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
    
    def has_add_permission(self, request):
        """
        Отключает возможность добавления через эту форму.
        
        Telegram профили должны создаваться только через форму пользователя.
        """
        return False

