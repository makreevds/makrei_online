import hashlib
import hmac
from typing import Optional, Dict, Any
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.conf import settings
from django import forms
from django.utils import timezone
from .models import TelegramProfile

class RegisterForm(forms.ModelForm):
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd.get('password') != cd.get('password2'):
            raise forms.ValidationError('Пароли не совпадают')
        return cd['password2']

def index(request: HttpRequest) -> HttpResponse:
    """Возвращает главную страницу сайта (index) через шаблон."""
    return render(request, "index.html")

def register(request: HttpRequest) -> HttpResponse:
    """Регистрация нового пользователя через форму."""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('index')
    else:
        form = RegisterForm()
    
    bot_username = getattr(settings, 'TELEGRAM_BOT_USERNAME', '').lstrip('@')
    bot_domain = getattr(settings, 'TELEGRAM_BOT_DOMAIN', '')
    
    # Формируем полный URL для callback
    if bot_domain:
        scheme = 'https' if not bot_domain.startswith('localhost') else 'http'
        telegram_callback_url = f"{scheme}://{bot_domain}/telegram-auth/"
    else:
        # Используем текущий домен из запроса
        scheme = 'https' if request.is_secure() else 'http'
        telegram_callback_url = f"{scheme}://{request.get_host()}/telegram-auth/"
    
    return render(request, 'register.html', {
        'form': form,
        'telegram_bot_username': bot_username,
        'telegram_callback_url': telegram_callback_url
    })

def login_view(request: HttpRequest) -> HttpResponse:
    """Вход пользователя с помощью стандартной формы аутентификации."""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    
    bot_username = getattr(settings, 'TELEGRAM_BOT_USERNAME', '').lstrip('@')
    bot_domain = getattr(settings, 'TELEGRAM_BOT_DOMAIN', '')
    
    # Формируем полный URL для callback
    if bot_domain:
        scheme = 'https' if not bot_domain.startswith('localhost') else 'http'
        telegram_callback_url = f"{scheme}://{bot_domain}/telegram-auth/"
    else:
        # Используем текущий домен из запроса
        scheme = 'https' if request.is_secure() else 'http'
        telegram_callback_url = f"{scheme}://{request.get_host()}/telegram-auth/"
    
    return render(request, 'login.html', {
        'form': form,
        'telegram_bot_username': bot_username,
        'telegram_callback_url': telegram_callback_url
    })

def logout_view(request: HttpRequest) -> HttpResponse:
    """Выход пользователя."""
    logout(request)
    return redirect('index')


def _verify_telegram_auth(data: Dict[str, Any], bot_token: str) -> bool:
    """
    Проверяет подлинность данных авторизации от Telegram.
    
    Согласно документации Telegram Login Widget:
    https://core.telegram.org/widgets/login#checking-authorization
    
    Args:
        data: Словарь с данными от Telegram Login Widget (включая 'hash')
        bot_token: Токен Telegram бота
        
    Returns:
        True если данные подлинные, False в противном случае
    """
    if 'hash' not in data:
        return False
    
    # Создаем копию данных без hash для проверки
    data_copy = {k: v for k, v in data.items() if k != 'hash'}
    received_hash = data['hash']
    
    # Создаем строку для проверки (все поля кроме hash, отсортированные по ключу)
    data_check_string = '\n'.join(
        f"{key}={value}" 
        for key, value in sorted(data_copy.items())
    )
    
    # Вычисляем секретный ключ из токена бота
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    
    # Вычисляем HMAC-SHA256
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return calculated_hash == received_hash


def telegram_auth(request: HttpRequest) -> HttpResponse:
    """
    Обрабатывает callback от Telegram Login Widget.
    
    Создает или обновляет пользователя на основе данных из Telegram,
    авторизует его и перенаправляет на главную страницу.
    """
    if request.method != 'GET':
        return HttpResponseBadRequest("Только GET запросы разрешены")
    
    # Получаем данные от Telegram
    telegram_data = {
        'id': request.GET.get('id'),
        'first_name': request.GET.get('first_name', ''),
        'last_name': request.GET.get('last_name', ''),
        'username': request.GET.get('username', ''),
        'photo_url': request.GET.get('photo_url', ''),
        'auth_date': request.GET.get('auth_date'),
        'hash': request.GET.get('hash'),
    }
    
    # Проверяем наличие обязательных полей
    if not telegram_data['id'] or not telegram_data['auth_date'] or not telegram_data['hash']:
        return HttpResponseBadRequest("Отсутствуют обязательные данные")
    
    # Получаем токен бота из настроек
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    if not bot_token:
        return HttpResponseBadRequest("Telegram Bot Token не настроен")
    
    # Проверяем подлинность данных
    if not _verify_telegram_auth(telegram_data.copy(), bot_token):
        return HttpResponseBadRequest("Неверная подпись данных")
    
    # Проверяем срок действия авторизации (не старше 24 часов)
    try:
        auth_date = int(telegram_data['auth_date'])
        current_timestamp = int(timezone.now().timestamp())
        if current_timestamp - auth_date > 86400:  # 24 часа
            return HttpResponseBadRequest("Срок действия авторизации истек")
    except (ValueError, TypeError):
        return HttpResponseBadRequest("Неверный формат даты авторизации")
    
    telegram_id = int(telegram_data['id'])
    
    # Ищем существующий профиль Telegram
    try:
        telegram_profile = TelegramProfile.objects.get(telegram_id=telegram_id)
        user = telegram_profile.user
        
        # Обновляем данные профиля
        telegram_profile.first_name = telegram_data['first_name']
        telegram_profile.last_name = telegram_data['last_name'] or None
        telegram_profile.username = telegram_data['username'] or None
        telegram_profile.photo_url = telegram_data['photo_url'] or None
        telegram_profile.save()
        
    except TelegramProfile.DoesNotExist:
        # Создаем нового пользователя
        # Генерируем уникальное имя пользователя
        base_username = telegram_data['username'] or f"tg_{telegram_id}"
        username = base_username
        counter = 1
        
        # Убеждаемся, что username уникален
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1
        
        # Создаем пользователя
        user = User.objects.create_user(
            username=username,
            first_name=telegram_data['first_name'],
            last_name=telegram_data['last_name'] or '',
            email='',  # Email не обязателен для Telegram авторизации
        )
        
        # Создаем профиль Telegram
        telegram_profile = TelegramProfile.objects.create(
            user=user,
            telegram_id=telegram_id,
            first_name=telegram_data['first_name'],
            last_name=telegram_data['last_name'] or None,
            username=telegram_data['username'] or None,
            photo_url=telegram_data['photo_url'] or None,
        )
    
    # Авторизуем пользователя
    login(request, user)
    
    # Перенаправляем на главную страницу
    return redirect('index')
