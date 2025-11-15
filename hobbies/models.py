"""Модели для управления хобби и постами."""
from django.db import models
from django.urls import reverse
from typing import Optional


class Hobby(models.Model):
    """
    Модель хобби.
    
    Хранит информацию о каждом хобби пользователя.
    """
    
    title = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Название вашего хобби'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='URL-адрес',
        help_text='Уникальный идентификатор для URL'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание',
        help_text='Краткое описание хобби'
    )
    image = models.ImageField(
        upload_to='hobbies/',
        blank=True,
        null=True,
        verbose_name='Изображение',
        help_text='Изображение для хобби'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
        db_index=True
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    
    class Meta:
        verbose_name = 'Хобби'
        verbose_name_plural = 'Хобби'
        ordering = ['-created_at']
        db_table = 'hobbies'
    
    def __str__(self) -> str:
        """Возвращает строковое представление хобби."""
        return self.title
    
    def get_absolute_url(self) -> str:
        """Возвращает URL для детального просмотра хобби."""
        return reverse('hobbies:detail', kwargs={'slug': self.slug})


class Entry(models.Model):
    """
    Модель поста.
    
    Хранит посты, связанные с хобби.
    """
    
    hobby = models.ForeignKey(
        Hobby,
        on_delete=models.CASCADE,
        related_name='entries',
        verbose_name='Хобби',
        db_index=True
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок',
        help_text='Заголовок поста'
    )
    content = models.TextField(
        verbose_name='Содержание',
        help_text='Текст поста'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
        db_index=True
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления',
        db_index=True
    )
    
    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-created_at']
        db_table = 'entries'
        indexes = [
            models.Index(fields=['hobby', '-created_at']),
        ]
    
    def __str__(self) -> str:
        """Возвращает строковое представление поста."""
        return self.title
    
    def get_absolute_url(self) -> str:
        """Возвращает URL для детального просмотра поста."""
        return reverse(
            'hobbies:entry_detail',
            kwargs={'slug': self.hobby.slug, 'pk': self.pk}
        )


class EntryImage(models.Model):
    """
    Модель изображения в посте.
    
    Хранит изображения, прикрепленные к постам.
    """
    
    entry = models.ForeignKey(
        Entry,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Пост',
        db_index=True
    )
    image = models.ImageField(
        upload_to='entries/',
        verbose_name='Изображение',
        help_text='Изображение для поста'
    )
    caption = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Подпись',
        help_text='Подпись к изображению (необязательно)'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Порядок',
        help_text='Порядок отображения изображения (меньше = выше)',
        db_index=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления',
        db_index=True
    )
    
    class Meta:
        verbose_name = 'Изображение поста'
        verbose_name_plural = 'Изображения постов'
        ordering = ['order', 'created_at']
        db_table = 'entry_images'
    
    def __str__(self) -> str:
        """Возвращает строковое представление изображения."""
        if self.caption:
            return f'{self.entry.title} - {self.caption}'
        return f'{self.entry.title} - Изображение #{self.order}'
