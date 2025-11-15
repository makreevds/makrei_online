"""Админ-панель для управления паролями."""
from django.contrib import admin
from .models import PasswordEntry


@admin.register(PasswordEntry)
class PasswordEntryAdmin(admin.ModelAdmin):
    """Административный интерфейс для записей паролей."""
    
    list_display = ['service', 'login', 'email', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['service', 'login', 'email']
    readonly_fields = ['created_at', 'updated_at', 'password_encrypted']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('service', 'login', 'email')
        }),
        ('Пароль', {
            'fields': ('password_encrypted',),
            'description': 'Пароль хранится в зашифрованном виде. '
                          'Для просмотра используйте веб-интерфейс с мастер-паролем.'
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
