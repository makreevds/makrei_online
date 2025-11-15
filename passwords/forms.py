"""Формы для работы с паролями."""
from typing import Optional
from django import forms
from django.core.exceptions import ValidationError
from .models import PasswordEntry
from .utils import encrypt_password, decrypt_password


class MasterPasswordSetupForm(forms.Form):
    """Форма для установки мастер-пароля (при первом использовании)."""
    
    master_password = forms.CharField(
        label='Мастер-пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Придумайте мастер-пароль',
            'autocomplete': 'off'
        }),
        required=True,
        min_length=8,
        help_text='Минимум 8 символов. Этот пароль будет использоваться для шифрования всех ваших паролей.'
    )
    
    master_password_confirm = forms.CharField(
        label='Подтверждение мастер-пароля',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Повторите мастер-пароль',
            'autocomplete': 'off'
        }),
        required=True,
        help_text='Повторите мастер-пароль для подтверждения'
    )
    
    def clean(self) -> dict:
        """Проверяет совпадение паролей."""
        cleaned_data = super().clean()
        password = cleaned_data.get('master_password')
        password_confirm = cleaned_data.get('master_password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise ValidationError({
                'master_password_confirm': 'Пароли не совпадают. Пожалуйста, введите одинаковые пароли.'
            })
        
        return cleaned_data


class MasterPasswordForm(forms.Form):
    """Форма для ввода мастер-пароля."""
    
    master_password = forms.CharField(
        label='Мастер-пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите мастер-пароль для расшифровки',
            'autocomplete': 'off'
        }),
        required=True,
        help_text='Введите контрольную фразу для доступа к паролям'
    )


class MasterPasswordChangeForm(forms.Form):
    """Форма для смены мастер-пароля."""
    
    old_master_password = forms.CharField(
        label='Текущий мастер-пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите текущий мастер-пароль',
            'autocomplete': 'off'
        }),
        required=True,
        help_text='Введите текущий мастер-пароль для подтверждения'
    )
    
    new_master_password = forms.CharField(
        label='Новый мастер-пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Придумайте новый мастер-пароль',
            'autocomplete': 'off'
        }),
        required=True,
        min_length=8,
        help_text='Минимум 8 символов. Этот пароль будет использоваться для шифрования всех ваших паролей.'
    )
    
    new_master_password_confirm = forms.CharField(
        label='Подтверждение нового мастер-пароля',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Повторите новый мастер-пароль',
            'autocomplete': 'off'
        }),
        required=True,
        help_text='Повторите новый мастер-пароль для подтверждения'
    )
    
    def clean(self) -> dict:
        """Проверяет совпадение новых паролей."""
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_master_password')
        new_password_confirm = cleaned_data.get('new_master_password_confirm')
        
        if new_password and new_password_confirm and new_password != new_password_confirm:
            raise ValidationError({
                'new_master_password_confirm': 'Новые пароли не совпадают. Пожалуйста, введите одинаковые пароли.'
            })
        
        return cleaned_data


class PasswordEntryForm(forms.ModelForm):
    """Форма для создания и редактирования записи пароля."""
    
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль',
            'autocomplete': 'off'
        }),
        required=False,
        help_text='Пароль будет зашифрован перед сохранением. Оставьте пустым, если не хотите менять пароль.'
    )
    
    class Meta:
        model = PasswordEntry
        fields = ['service', 'login', 'email']
        widgets = {
            'service': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название сайта или сервиса'
            }),
            'login': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Логин или email'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email (необязательно)'
            }),
        }
        labels = {
            'service': 'Сервис',
            'login': 'Логин',
            'email': 'Email',
        }
    
    def save(self, commit: bool = True, master_password: Optional[str] = None) -> PasswordEntry:
        """
        Сохраняет запись с зашифрованным паролем.
        
        Args:
            commit: Сохранять ли объект в базу данных
            master_password: Мастер-пароль для шифрования (должен быть передан из сессии)
        
        Returns:
            PasswordEntry: Сохранённый объект записи пароля
        """
        if not master_password:
            raise ValueError('Мастер-пароль должен быть указан для шифрования пароля.')
        
        instance = super().save(commit=False)
        password = self.cleaned_data.get('password')
        
        # Шифруем пароль только если он указан
        if password:
            instance.password_encrypted = encrypt_password(password, master_password)
        # Если пароль не указан и это редактирование, оставляем старый
        
        if commit:
            instance.save()
        return instance
    
    def clean(self) -> dict:
        """Валидация формы."""
        cleaned_data = super().clean()
        service = cleaned_data.get('service')
        login = cleaned_data.get('login')
        password = cleaned_data.get('password')
        
        if not service or not service.strip():
            raise ValidationError({'service': 'Поле "Сервис" обязательно для заполнения.'})
        
        if not login or not login.strip():
            raise ValidationError({'login': 'Поле "Логин" обязательно для заполнения.'})
        
        # При создании новой записи пароль обязателен
        if not self.instance.pk and (not password or not password.strip()):
            raise ValidationError({'password': 'Поле "Пароль" обязательно для заполнения при создании новой записи.'})
        
        return cleaned_data

