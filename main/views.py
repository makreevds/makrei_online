from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django import forms

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
    
    return render(request, 'register.html', {
        'form': form,
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
    
    return render(request, 'login.html', {
        'form': form,
    })

def logout_view(request: HttpRequest) -> HttpResponse:
    """Выход пользователя."""
    logout(request)
    return redirect('index')
