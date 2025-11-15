"""Кастомные теги шаблонов для работы с паролями."""
from django import template

register = template.Library()


@register.filter
def get_item(dictionary: dict, key) -> str:
    """
    Получает значение из словаря по ключу.
    
    Использование: {{ dictionary|get_item:key }}
    """
    if dictionary is None:
        return ''
    return dictionary.get(key, '')

