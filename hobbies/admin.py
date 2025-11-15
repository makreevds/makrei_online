"""Административный интерфейс для моделей хобби."""
from django.contrib import admin
from django.utils.html import format_html
from typing import Optional

from .models import Hobby, Entry, EntryImage


@admin.register(Hobby)
class HobbyAdmin(admin.ModelAdmin):
    """Административный интерфейс для модели Hobby."""
    
    list_display = ['title', 'slug', 'entry_count', 'created_at', 'image_preview']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['title', 'description', 'slug']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at', 'image_preview']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'description')
        }),
        ('Медиа', {
            'fields': ('image', 'image_preview')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def entry_count(self, obj: Hobby) -> int:
        """Возвращает количество постов для хобби."""
        return obj.entries.count()
    entry_count.short_description = 'Постов'
    
    def image_preview(self, obj: Hobby) -> Optional[str]:
        """Отображает превью изображения."""
        if obj.image:
            return format_html(
                '<img src="{}" width="200" height="200" style="object-fit: cover;" />',
                obj.image.url
            )
        return 'Нет изображения'
    image_preview.short_description = 'Превью'


class EntryImageInline(admin.TabularInline):
    """Инлайн-редактирование изображений в админке поста."""
    
    model = EntryImage
    extra = 1
    fields = ['image', 'caption', 'order']
    ordering = ['order', 'created_at']


class EntryInline(admin.TabularInline):
    """Инлайн-редактирование постов в админке хобби."""
    
    model = Entry
    extra = 0
    fields = ['title', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    """Административный интерфейс для модели Entry."""
    
    list_display = ['title', 'hobby', 'image_count', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at', 'hobby']
    search_fields = ['title', 'content']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    inlines = [EntryImageInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('hobby', 'title', 'content')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Оптимизация запросов с использованием select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related('hobby')
    
    def image_count(self, obj: Entry) -> int:
        """Возвращает количество изображений в посте."""
        return obj.images.count()
    image_count.short_description = 'Изображений'


@admin.register(EntryImage)
class EntryImageAdmin(admin.ModelAdmin):
    """Административный интерфейс для модели EntryImage."""
    
    list_display = ['entry', 'image_preview', 'caption', 'order', 'created_at']
    list_filter = ['created_at', 'entry__hobby']
    search_fields = ['entry__title', 'caption']
    readonly_fields = ['created_at', 'image_preview']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('entry', 'image', 'caption', 'order')
        }),
        ('Превью', {
            'fields': ('image_preview',)
        }),
        ('Метаданные', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Оптимизация запросов с использованием select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related('entry', 'entry__hobby')
    
    def image_preview(self, obj: EntryImage) -> Optional[str]:
        """Отображает превью изображения."""
        if obj.image:
            return format_html(
                '<img src="{}" width="200" height="200" style="object-fit: cover;" />',
                obj.image.url
            )
        return 'Нет изображения'
    image_preview.short_description = 'Превью'
