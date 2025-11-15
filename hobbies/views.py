"""Представления для отображения хобби и постов."""
from typing import Optional
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import QuerySet, Count
from django.http import HttpRequest, HttpResponse

from .models import Hobby, Entry


class HobbyListView(ListView):
    """
    Список всех хобби.
    
    Отображает все хобби пользователя с количеством постов.
    """
    
    model = Hobby
    template_name = 'hobbies/hobby_list.html'
    context_object_name = 'hobbies'
    paginate_by = 12
    
    def get_queryset(self) -> QuerySet[Hobby]:
        """Возвращает список хобби с количеством постов."""
        return Hobby.objects.annotate(
            entries_count=Count('entries')
        ).prefetch_related('entries').order_by('-created_at')


class HobbyDetailView(DetailView):
    """
    Детальный просмотр хобби.
    
    Отображает информацию о хобби и все связанные посты.
    """
    
    model = Hobby
    template_name = 'hobbies/hobby_detail.html'
    context_object_name = 'hobby'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self) -> QuerySet[Hobby]:
        """Возвращает хобби с предзагруженными постами."""
        return Hobby.objects.prefetch_related('entries')
    
    def get_context_data(self, **kwargs) -> dict:
        """Добавляет посты в контекст."""
        context = super().get_context_data(**kwargs)
        hobby = self.get_object()
        
        # Получаем все посты для хобби
        entries = hobby.entries.all().prefetch_related('images').order_by('-created_at')
        context['entries'] = entries
        
        return context


class EntryDetailView(DetailView):
    """
    Детальный просмотр поста.
    
    Отображает полную информацию о посте с изображениями.
    """
    
    model = Entry
    template_name = 'hobbies/entry_detail.html'
    context_object_name = 'entry'
    pk_url_kwarg = 'pk'
    
    def get_queryset(self) -> QuerySet[Entry]:
        """Возвращает пост с предзагруженным хобби и изображениями."""
        return Entry.objects.select_related('hobby').prefetch_related('images')
    
    def get_object(self, queryset: Optional[QuerySet[Entry]] = None) -> Entry:
        """Получает пост по slug хобби и pk поста."""
        hobby_slug = self.kwargs.get('slug')
        pk = self.kwargs.get(self.pk_url_kwarg)
        
        hobby = get_object_or_404(Hobby, slug=hobby_slug)
        entry = get_object_or_404(Entry, pk=pk, hobby=hobby)
        return entry
    
    def get_context_data(self, **kwargs) -> dict:
        """Добавляет связанные посты и изображения в контекст."""
        context = super().get_context_data(**kwargs)
        entry = self.get_object()
        
        # Получаем изображения поста, отсортированные по порядку
        context['images'] = entry.images.all().order_by('order', 'created_at')
        
        # Получаем предыдущий и следующий посты того же хобби
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
