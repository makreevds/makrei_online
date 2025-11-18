"""Представления для отображения проектов и постов."""
from typing import Optional
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.views.decorators.http import require_http_methods
from django.db.models import QuerySet, Count
from django.http import HttpRequest, HttpResponse

from .models import Hobby, Entry
from .forms import HobbyForm, EntryForm


class HobbyListView(LoginRequiredMixin, ListView):
    """
    Список всех проектов.
    
    Отображает все проекты текущего пользователя с количеством постов.
    """
    
    model = Hobby
    template_name = 'hobbies/hobby_list.html'
    context_object_name = 'hobbies'
    paginate_by = 12
    
    def get_queryset(self) -> QuerySet[Hobby]:
        """Возвращает список проектов текущего пользователя с количеством постов."""
        return Hobby.objects.filter(
            user=self.request.user
        ).annotate(
            entries_count=Count('entries')
        ).prefetch_related('entries').order_by('-created_at')


class HobbyDetailView(LoginRequiredMixin, DetailView):
    """
    Детальный просмотр проекта.
    
    Отображает информацию о проекте и все связанные посты.
    """
    
    model = Hobby
    template_name = 'hobbies/hobby_detail.html'
    context_object_name = 'hobby'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self) -> QuerySet[Hobby]:
        """Возвращает проекты текущего пользователя с предзагруженными постами."""
        return Hobby.objects.filter(
            user=self.request.user
        ).prefetch_related('entries')
    
    def get_context_data(self, **kwargs) -> dict:
        """Добавляет посты в контекст."""
        context = super().get_context_data(**kwargs)
        hobby = self.get_object()
        
        # Получаем все посты для проекта, отсортированные по дате (свежие сверху)
        # Используем prefetch_related для оптимизации запросов к изображениям
        entries = hobby.entries.all().prefetch_related(
            'images'
        ).order_by('-created_at')
        context['entries'] = entries
        
        return context


class EntryDetailView(LoginRequiredMixin, DetailView):
    """
    Детальный просмотр поста.
    
    Отображает полную информацию о посте с изображениями.
    """
    
    model = Entry
    template_name = 'hobbies/entry_detail.html'
    context_object_name = 'entry'
    pk_url_kwarg = 'pk'
    
    def get_queryset(self) -> QuerySet[Entry]:
        """Возвращает посты текущего пользователя с предзагруженным проектом и изображениями."""
        return Entry.objects.filter(
            hobby__user=self.request.user
        ).select_related('hobby').prefetch_related('images')
    
    def get_object(self, queryset: Optional[QuerySet[Entry]] = None) -> Entry:
        """Получает пост по slug проекта и pk поста."""
        hobby_slug = self.kwargs.get('slug')
        pk = self.kwargs.get(self.pk_url_kwarg)
        
        hobby = get_object_or_404(Hobby, slug=hobby_slug, user=self.request.user)
        entry = get_object_or_404(Entry, pk=pk, hobby=hobby)
        return entry
    
    def get_context_data(self, **kwargs) -> dict:
        """Добавляет связанные посты и изображения в контекст."""
        context = super().get_context_data(**kwargs)
        entry = self.get_object()
        
        # Получаем изображения поста, отсортированные по порядку
        context['images'] = entry.images.all().order_by('order', 'created_at')
        
        # Получаем предыдущий и следующий посты того же проекта
        all_entries = entry.hobby.entries.order_by('-created_at')
        entry_list = list(all_entries)
        
        try:
            current_index = entry_list.index(entry)
            context['prev_entry'] = entry_list[current_index + 1] if current_index + 1 < len(entry_list) else None
            context['next_entry'] = entry_list[current_index - 1] if current_index > 0 else None
        except ValueError:
            context['prev_entry'] = None
            context['next_entry'] = None
        
        return context


def index(request: HttpRequest) -> HttpResponse:
    """
    Главная страница сайта.
    
    Отображает приветственную страницу.
    """
    return render(request, 'hobbies/index.html')


# ========== CRUD для проектов ==========

@login_required
@require_http_methods(["GET", "POST"])
def hobby_create(request: HttpRequest) -> HttpResponse:
    """Создание нового проекта."""
    if request.method == 'POST':
        form = HobbyForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            hobby = form.save()
            messages.success(request, f'Проект "{hobby.title}" успешно создан!')
            return redirect('hobbies:detail', slug=hobby.slug)
    else:
        form = HobbyForm(user=request.user)
    
    return render(request, 'hobbies/hobby_form.html', {
        'form': form,
        'title': 'Создать проект',
    })


@login_required
@require_http_methods(["GET", "POST"])
def hobby_update(request: HttpRequest, slug: str) -> HttpResponse:
    """Редактирование проекта."""
    hobby = get_object_or_404(Hobby, slug=slug, user=request.user)
    
    if request.method == 'POST':
        form = HobbyForm(request.POST, request.FILES, instance=hobby, user=request.user)
        if form.is_valid():
            hobby = form.save()
            messages.success(request, f'Проект "{hobby.title}" успешно обновлён!')
            return redirect('hobbies:detail', slug=hobby.slug)
    else:
        form = HobbyForm(instance=hobby, user=request.user)
    
    return render(request, 'hobbies/hobby_form.html', {
        'form': form,
        'hobby': hobby,
        'title': 'Редактировать проект',
    })


@login_required
@require_http_methods(["POST"])
def hobby_delete(request: HttpRequest, slug: str) -> HttpResponse:
    """Удаление проекта."""
    hobby = get_object_or_404(Hobby, slug=slug, user=request.user)
    hobby_title = hobby.title
    hobby.delete()
    messages.success(request, f'Проект "{hobby_title}" успешно удалён!')
    return redirect('hobbies:list')


# ========== CRUD для постов ==========

@login_required
@require_http_methods(["GET", "POST"])
def entry_create(request: HttpRequest, slug: Optional[str] = None) -> HttpResponse:
    """Создание нового поста."""
    hobby = None
    if slug:
        hobby = get_object_or_404(Hobby, slug=slug, user=request.user)
    
    if request.method == 'POST':
        form = EntryForm(request.POST, user=request.user, hobby=slug)
        if form.is_valid():
            entry = form.save()
            messages.success(request, f'Пост "{entry.title}" успешно создан!')
            return redirect('hobbies:detail', slug=entry.hobby.slug)
    else:
        form = EntryForm(user=request.user, hobby=slug)
    
    return render(request, 'hobbies/entry_form.html', {
        'form': form,
        'hobby': hobby,
        'title': 'Создать пост',
    })


@login_required
@require_http_methods(["GET", "POST"])
def entry_update(request: HttpRequest, slug: str, pk: int) -> HttpResponse:
    """Редактирование поста."""
    hobby = get_object_or_404(Hobby, slug=slug, user=request.user)
    entry = get_object_or_404(Entry, pk=pk, hobby=hobby)
    
    if request.method == 'POST':
        form = EntryForm(request.POST, instance=entry, user=request.user)
        if form.is_valid():
            entry = form.save()
            messages.success(request, f'Пост "{entry.title}" успешно обновлён!')
            return redirect('hobbies:detail', slug=entry.hobby.slug)
    else:
        form = EntryForm(instance=entry, user=request.user)
    
    return render(request, 'hobbies/entry_form.html', {
        'form': form,
        'entry': entry,
        'hobby': hobby,
        'title': 'Редактировать пост',
    })


@login_required
@require_http_methods(["POST"])
def entry_delete(request: HttpRequest, slug: str, pk: int) -> HttpResponse:
    """Удаление поста."""
    hobby = get_object_or_404(Hobby, slug=slug, user=request.user)
    entry = get_object_or_404(Entry, pk=pk, hobby=hobby)
    entry_title = entry.title
    hobby_slug = entry.hobby.slug
    entry.delete()
    messages.success(request, f'Пост "{entry_title}" успешно удалён!')
    return redirect('hobbies:detail', slug=hobby_slug)
