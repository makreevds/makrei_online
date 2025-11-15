"""Представления для работы с паролями."""
from typing import Optional
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.db.models import QuerySet
from .models import PasswordEntry
from .forms import MasterPasswordForm, PasswordEntryForm
from .utils import decrypt_password


@require_http_methods(["GET", "POST"])
def password_list(request: HttpRequest) -> HttpResponse:
    """
    Список всех паролей.
    
    Требует ввода мастер-пароля для расшифровки.
    """
    entries: Optional[QuerySet[PasswordEntry]] = None
    decrypted_passwords: dict[int, str] = {}
    form = MasterPasswordForm()
    
    if request.method == 'POST':
        form = MasterPasswordForm(request.POST)
        if form.is_valid():
            master_password = form.cleaned_data['master_password']
            entries = PasswordEntry.objects.all().order_by('-created_at')
            
            # Расшифровываем пароли
            for entry in entries:
                decrypted = decrypt_password(entry.password_encrypted, master_password)
                if decrypted:
                    decrypted_passwords[entry.id] = decrypted
                else:
                    messages.error(
                        request,
                        f'Не удалось расшифровать пароль для {entry.service}. '
                        'Проверьте правильность мастер-пароля.'
                    )
                    return render(request, 'passwords/password_list.html', {
                        'form': form,
                        'entries': None,
                        'decrypted_passwords': {},
                    })
            
            # Сохраняем мастер-пароль в сессии для текущей сессии
            request.session['master_password_verified'] = True
            request.session['master_password'] = master_password
    
    # Если мастер-пароль уже введён в этой сессии
    if request.session.get('master_password_verified'):
        master_password = request.session.get('master_password')
        if master_password:
            entries = PasswordEntry.objects.all().order_by('-created_at')
            for entry in entries:
                decrypted = decrypt_password(entry.password_encrypted, master_password)
                if decrypted:
                    decrypted_passwords[entry.id] = decrypted
    
    return render(request, 'passwords/password_list.html', {
        'form': form,
        'entries': entries,
        'decrypted_passwords': decrypted_passwords,
    })


@require_http_methods(["GET", "POST"])
def password_create(request: HttpRequest) -> HttpResponse:
    """Создание новой записи пароля."""
    if request.method == 'POST':
        form = PasswordEntryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пароль успешно сохранён!')
            return redirect('passwords:list')
    else:
        form = PasswordEntryForm()
    
    return render(request, 'passwords/password_form.html', {
        'form': form,
        'title': 'Добавить пароль',
    })


@require_http_methods(["GET", "POST"])
def password_update(request: HttpRequest, pk: int) -> HttpResponse:
    """Редактирование записи пароля."""
    entry = get_object_or_404(PasswordEntry, pk=pk)
    
    if request.method == 'POST':
        form = PasswordEntryForm(request.POST, instance=entry)
        if form.is_valid():
            # Если пароль не указан, сохраняем старый зашифрованный пароль
            if not form.cleaned_data.get('password'):
                form.instance.password_encrypted = entry.password_encrypted
            form.save()
            messages.success(request, 'Пароль успешно обновлён!')
            return redirect('passwords:list')
    else:
        form = PasswordEntryForm(instance=entry)
    
    return render(request, 'passwords/password_form.html', {
        'form': form,
        'entry': entry,
        'title': 'Редактировать пароль',
    })


@require_http_methods(["POST"])
def password_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """Удаление записи пароля."""
    entry = get_object_or_404(PasswordEntry, pk=pk)
    entry.delete()
    messages.success(request, 'Пароль успешно удалён!')
    return redirect('passwords:list')


@require_http_methods(["POST"])
def clear_session(request: HttpRequest) -> HttpResponse:
    """Очистка сессии (забыть мастер-пароль)."""
    request.session.pop('master_password_verified', None)
    request.session.pop('master_password', None)
    messages.info(request, 'Сессия очищена. Мастер-пароль забыт.')
    return redirect('passwords:list')
