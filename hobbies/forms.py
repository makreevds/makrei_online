"""Формы для работы с проектами и постами."""
from typing import Optional
from django import forms
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from .models import Hobby, Entry


class HobbyForm(forms.ModelForm):
    """
    Форма для создания и редактирования проекта.
    
    Автоматически генерирует slug из названия, если он не указан.
    """
    
    class Meta:
        model = Hobby
        fields = ['title', 'slug', 'description', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название проекта'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'url-адрес (автоматически)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Описание проекта (необязательно)'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
        labels = {
            'title': 'Название',
            'slug': 'URL-адрес',
            'description': 'Описание',
            'image': 'Изображение',
        }
        help_texts = {
            'slug': 'Уникальный идентификатор для URL. Оставьте пустым для автоматической генерации.',
            'description': 'Краткое описание проекта (необязательно)',
            'image': 'Изображение для проекта (необязательно)',
        }
    
    def clean_slug(self) -> str:
        """Генерирует slug из названия, если он не указан."""
        slug = self.cleaned_data.get('slug')
        title = self.cleaned_data.get('title')
        
        # Если slug не указан, он будет сгенерирован в методе save()
        # Здесь только проверяем уникальность, если slug указан
        if slug:
            hobby = Hobby.objects.filter(
                user=self.user,
                slug=slug
            ).exclude(pk=self.instance.pk if self.instance.pk else None)
            
            if hobby.exists():
                raise ValidationError('Проект с таким URL-адресом уже существует.')
        
        return slug
    
    def __init__(self, *args, user=None, **kwargs):
        """Инициализирует форму с пользователем."""
        super().__init__(*args, **kwargs)
        self.user = user
        # Делаем slug необязательным при создании
        if not self.instance.pk:
            self.fields['slug'].required = False
    
    def save(self, commit: bool = True) -> Hobby:
        """Сохраняет проект с привязкой к пользователю."""
        instance = super().save(commit=False)
        if self.user:
            instance.user = self.user
        
        # Генерируем slug, если он не указан
        if not instance.slug and instance.title:
            base_slug = slugify(instance.title)
            slug = base_slug
            counter = 1
            while Hobby.objects.filter(user=instance.user, slug=slug).exclude(
                pk=instance.pk if instance.pk else None
            ).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            instance.slug = slug
        
        if commit:
            instance.save()
        return instance


class EntryForm(forms.ModelForm):
    """
    Форма для создания и редактирования поста.
    
    Позволяет выбрать проект из списка проектов пользователя.
    """
    
    class Meta:
        model = Entry
        fields = ['hobby', 'title', 'content']
        widgets = {
            'hobby': forms.Select(attrs={
                'class': 'form-control'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Заголовок поста'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Содержание поста'
            }),
        }
        labels = {
            'hobby': 'Проект',
            'title': 'Заголовок',
            'content': 'Содержание',
        }
    
    def __init__(self, *args, user=None, hobby=None, **kwargs):
        """Инициализирует форму с пользователем и фильтрует проекты."""
        super().__init__(*args, **kwargs)
        self.user = user
        
        # Фильтруем проекты только текущего пользователя
        if user:
            self.fields['hobby'].queryset = Hobby.objects.filter(user=user).order_by('title')
        
        # Если передан hobby, устанавливаем его по умолчанию
        if hobby and user:
            hobby_obj = Hobby.objects.filter(user=user, slug=hobby).first()
            if hobby_obj:
                self.fields['hobby'].initial = hobby_obj
    
    def clean_hobby(self) -> Hobby:
        """Проверяет, что проект принадлежит пользователю."""
        hobby = self.cleaned_data.get('hobby')
        if hobby and self.user and hobby.user != self.user:
            raise ValidationError('Вы не можете добавлять посты в чужие проекты.')
        return hobby
    
    def save(self, commit: bool = True) -> Entry:
        """Сохраняет пост."""
        instance = super().save(commit=commit)
        return instance

