"""Представления для регистрации и входа пользователей."""
from typing import Optional
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import HttpRequest, HttpResponse

from .forms import UserRegistrationForm, UserLoginForm


@require_http_methods(["GET", "POST"])
def register_view(request: HttpRequest) -> HttpResponse:
    """
    Представление для регистрации нового пользователя.
    
    Если пользователь уже авторизован, перенаправляет на главную страницу.
    """
    if request.user.is_authenticated:
        messages.info(request, 'Вы уже авторизованы.')
        return redirect('index')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f'Регистрация успешна! Добро пожаловать, {user.username}!'
            )
            login(request, user)
            return redirect('index')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {
        'form': form,
    })


@require_http_methods(["GET", "POST"])
def login_view(request: HttpRequest) -> HttpResponse:
    """
    Представление для входа пользователя.
    
    Если пользователь уже авторизован, перенаправляет на главную страницу.
    """
    if request.user.is_authenticated:
        messages.info(request, 'Вы уже авторизованы.')
        return redirect('index')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            
            # Перенаправление на страницу, с которой пришел пользователь, или на главную
            next_url = request.GET.get('next', 'index')
            return redirect(next_url)
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {
        'form': form,
        'next': request.GET.get('next', ''),
    })


@login_required
@require_http_methods(["POST"])
def logout_view(request: HttpRequest) -> HttpResponse:
    """
    Представление для выхода пользователя.
    
    Требует авторизации.
    """
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('index')
