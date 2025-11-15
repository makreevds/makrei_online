"""Формы для работы с паролями."""
from typing import Optional
from django import forms
from django.core.exceptions import ValidationError
from .models import PasswordEntry
from .utils import encrypt_password, decrypt_password


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
    master_password = forms.CharField(
        label='Мастер-пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите мастер-пароль для шифрования',
            'autocomplete': 'off'
        }),
        required=True,
        help_text='Мастер-пароль для шифрования пароля'
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
    
    def save(self, commit: bool = True) -> PasswordEntry:
        """Сохраняет запись с зашифрованным паролем."""
        instance = super().save(commit=False)
        master_password = self.cleaned_data['master_password']
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
        
        # Мастер-пароль обязателен
        master_password = cleaned_data.get('master_password')
        if not master_password or not master_password.strip():
            raise ValidationError({'master_password': 'Поле "Мастер-пароль" обязательно для заполнения.'})
        
        return cleaned_data

