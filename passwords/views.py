"""Представления для работы с паролями."""
from typing import Optional
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.db.models import QuerySet
from .models import PasswordEntry
from .forms import MasterPasswordForm, MasterPasswordSetupForm, MasterPasswordChangeForm, PasswordEntryForm
from .utils import decrypt_password, encrypt_password


@require_http_methods(["GET", "POST"])
def password_list(request: HttpRequest) -> HttpResponse:
    """
    Список всех паролей.
    
    Если паролей нет - показывает форму для создания мастер-пароля.
    Если пароли есть - требует ввода мастер-пароля для расшифровки.
    """
    entries: Optional[QuerySet[PasswordEntry]] = None
    decrypted_passwords: dict[int, str] = {}
    
    # Проверяем, есть ли уже пароли в базе
    has_passwords = PasswordEntry.objects.exists()
    
    # Если паролей нет - показываем форму для установки мастер-пароля
    if not has_passwords:
        setup_form = MasterPasswordSetupForm()
        
        if request.method == 'POST':
            setup_form = MasterPasswordSetupForm(request.POST)
            if setup_form.is_valid():
                master_password = setup_form.cleaned_data['master_password']
                # Сохраняем мастер-пароль в сессии для текущей сессии
                request.session['master_password_verified'] = True
                request.session['master_password'] = master_password
                messages.success(
                    request,
                    'Мастер-пароль успешно установлен! Теперь вы можете добавлять пароли.'
                )
                return render(request, 'passwords/password_list.html', {
                    'setup_form': setup_form,
                    'has_passwords': False,
                    'entries': None,
                    'decrypted_passwords': {},
                })
        
        return render(request, 'passwords/password_list.html', {
            'setup_form': setup_form,
            'has_passwords': False,
            'entries': None,
            'decrypted_passwords': {},
        })
    
    # Если пароли есть - показываем форму для ввода мастер-пароля
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
                        'has_passwords': True,
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
        'has_passwords': True,
        'entries': entries,
        'decrypted_passwords': decrypted_passwords,
    })


@require_http_methods(["GET", "POST"])
def password_create(request: HttpRequest) -> HttpResponse:
    """Создание новой записи пароля."""
    # Проверяем наличие мастер-пароля в сессии
    if not request.session.get('master_password_verified'):
        messages.error(
            request,
            'Для создания пароля необходимо сначала ввести мастер-пароль на странице списка паролей.'
        )
        return redirect('passwords:list')
    
    master_password = request.session.get('master_password')
    if not master_password:
        messages.error(
            request,
            'Мастер-пароль не найден в сессии. Пожалуйста, введите его снова.'
        )
        return redirect('passwords:list')
    
    if request.method == 'POST':
        form = PasswordEntryForm(request.POST)
        if form.is_valid():
            form.save(master_password=master_password)
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
    # Проверяем наличие мастер-пароля в сессии
    if not request.session.get('master_password_verified'):
        messages.error(
            request,
            'Для редактирования пароля необходимо сначала ввести мастер-пароль на странице списка паролей.'
        )
        return redirect('passwords:list')
    
    master_password = request.session.get('master_password')
    if not master_password:
        messages.error(
            request,
            'Мастер-пароль не найден в сессии. Пожалуйста, введите его снова.'
        )
        return redirect('passwords:list')
    
    entry = get_object_or_404(PasswordEntry, pk=pk)
    
    if request.method == 'POST':
        form = PasswordEntryForm(request.POST, instance=entry)
        if form.is_valid():
            # Если пароль не указан, сохраняем старый зашифрованный пароль
            if not form.cleaned_data.get('password'):
                form.instance.password_encrypted = entry.password_encrypted
            form.save(master_password=master_password)
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


@require_http_methods(["GET", "POST"])
def change_master_password(request: HttpRequest) -> HttpResponse:
    """
    Смена мастер-пароля.
    
    Требует ввода старого мастер-пароля для подтверждения.
    Перешифровывает все пароли новым мастер-паролем.
    """
    # Проверяем, есть ли пароли в базе
    has_passwords = PasswordEntry.objects.exists()
    if not has_passwords:
        messages.error(
            request,
            'Невозможно сменить мастер-пароль, так как паролей ещё нет.'
        )
        return redirect('passwords:list')
    
    form = MasterPasswordChangeForm()
    
    if request.method == 'POST':
        form = MasterPasswordChangeForm(request.POST)
        if form.is_valid():
            old_master_password = form.cleaned_data['old_master_password']
            new_master_password = form.cleaned_data['new_master_password']
            
            # Проверяем старый мастер-пароль - пытаемся расшифровать хотя бы один пароль
            entries = PasswordEntry.objects.all()
            test_entry = entries.first()
            
            if not test_entry:
                messages.error(request, 'Ошибка: не найдено паролей для проверки.')
                return redirect('passwords:list')
            
            decrypted_test = decrypt_password(test_entry.password_encrypted, old_master_password)
            if not decrypted_test:
                messages.error(
                    request,
                    'Неверный текущий мастер-пароль. Пожалуйста, проверьте правильность ввода.'
                )
                return render(request, 'passwords/change_master_password.html', {
                    'form': form,
                })
            
            # Старый пароль правильный - перешифровываем все пароли новым мастер-паролем
            success_count = 0
            error_count = 0
            
            for entry in entries:
                # Расшифровываем старым паролем
                decrypted = decrypt_password(entry.password_encrypted, old_master_password)
                if decrypted:
                    # Шифруем новым паролем
                    entry.password_encrypted = encrypt_password(decrypted, new_master_password)
                    entry.save()
                    success_count += 1
                else:
                    error_count += 1
            
            if error_count > 0:
                messages.warning(
                    request,
                    f'Мастер-пароль изменён, но не удалось перешифровать {error_count} паролей. '
                    'Проверьте их вручную.'
                )
            else:
                messages.success(
                    request,
                    f'Мастер-пароль успешно изменён! Перешифровано паролей: {success_count}.'
                )
            
            # Обновляем сессию с новым мастер-паролем
            request.session['master_password_verified'] = True
            request.session['master_password'] = new_master_password
            
            return redirect('passwords:list')
    
    return render(request, 'passwords/change_master_password.html', {
        'form': form,
    })
