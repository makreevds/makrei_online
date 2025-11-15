"""Кастомные шаблонные теги для отображения постов с изображениями."""
from django import template
from django.utils.safestring import mark_safe
from html import escape
import re
from typing import List, Dict

register = template.Library()


@register.filter
def first_sentences(text: str, count: int = 3) -> str:
    """
    Возвращает первые N предложений из текста.
    
    Args:
        text: Исходный текст
        count: Количество предложений (по умолчанию 3)
    
    Returns:
        str: Первые N предложений
    """
    if not text:
        return ''
    
    try:
        count = int(count)
    except (ValueError, TypeError):
        count = 3
    
    # Разбиваем текст на предложения по знакам препинания
    # Используем регулярное выражение для поиска предложений
    # Ищем предложения, заканчивающиеся на . ! ? с последующим пробелом или концом строки
    pattern = r'([^.!?]*[.!?]+(?:\s+|$))'
    matches = re.findall(pattern, text)
    
    if matches:
        # Берём первые count предложений
        result_sentences = matches[:count]
        return ' '.join(result_sentences).strip()
    
    # Если не нашли предложения через регулярку, используем простой метод
    # Разбиваем по точкам, восклицательным и вопросительным знакам
    simple_sentences = re.split(r'([.!?])', text)
    result_sentences = []
    current_sentence = ''
    
    for i, part in enumerate(simple_sentences):
        current_sentence += part
        if part in '.!?' and current_sentence.strip():
            result_sentences.append(current_sentence.strip())
            current_sentence = ''
            if len(result_sentences) >= count:
                break
    
    # Если всё ещё не хватает, добавляем оставшийся текст
    if len(result_sentences) < count and current_sentence.strip():
        result_sentences.append(current_sentence.strip())
    
    if result_sentences:
        return ' '.join(result_sentences[:count]).strip()
    
    # Если вообще не нашли предложений, возвращаем первые 200 символов
    return text[:200].strip() + '...' if len(text) > 200 else text.strip()


@register.simple_tag
def render_content_with_images(content: str, images: List) -> str:
    """
    Рендерит контент с изображениями.
    
    Поддерживает два способа вставки изображений:
    1. Через маркеры в тексте: [image:0], [image:1] и т.д. - будут заменены на изображения с соответствующим order
    2. Автоматически между абзацами, если маркеров нет - использует поле order из модели
    
    Args:
        content: Текст поста
        images: Список изображений (QuerySet или список EntryImage)
    
    Returns:
        HTML строка с текстом и изображениями
    """
    if not images:
        # Если нет изображений, просто возвращаем отформатированный текст
        escaped_content = escape(content)
        # Удаляем маркеры, если они есть
        escaped_content = re.sub(r'\[(?:image[:\s]*\d+|Изображение\s+с\s+order[:\s]*=?\s*\d+)\]\s*', '', escaped_content, flags=re.IGNORECASE)
        escaped_content = escaped_content.replace('\n\n', '</p><p>')
        escaped_content = escaped_content.replace('\n', '<br>')
        if escaped_content.strip():
            return mark_safe(f'<p>{escaped_content}</p>')
        return mark_safe('')
    
    # Сортируем изображения по полю order
    sorted_images = sorted(images, key=lambda img: img.order) if images else []
    
    # Создаём словарь для быстрого доступа к изображениям по order
    images_by_order = {}
    for img in sorted_images:
        order = img.order
        if order not in images_by_order:
            images_by_order[order] = []
        images_by_order[order].append(img)
    
    # Функция для генерации HTML изображения
    def get_image_html(order_val: int) -> str:
        """Генерирует HTML для изображений с указанным order."""
        if order_val not in images_by_order:
            return ''
        result = []
        for img in images_by_order[order_val]:
            img_html = '<div class="entry-image-inline">'
            img_html += f'<img src="{img.image.url}" alt="{escape(img.caption or "")}" loading="lazy">'
            if img.caption:
                img_html += f'<p class="image-caption-inline">{escape(img.caption)}</p>'
            img_html += '</div>'
            result.append(img_html)
        return ''.join(result)
    
    # Объединённый паттерн для поиска маркеров
    marker_pattern = r'\[(?:image[:\s]*(\d+)|Изображение\s+с\s+order[:\s]*=?\s*(\d+))\]'
    
    # Проверяем, есть ли маркеры в тексте
    has_markers = bool(re.search(marker_pattern, content, re.IGNORECASE | re.UNICODE))
    
    if has_markers:
        # Словарь для хранения плейсхолдеров и их HTML
        placeholders: Dict[str, str] = {}
        placeholder_counter = 0
        
        # Функция для замены маркера на плейсхолдер
        def replace_with_placeholder(match):
            nonlocal placeholder_counter
            order_str = match.group(1) or match.group(2)
            if order_str:
                try:
                    order = int(order_str)
                    image_html = get_image_html(order)
                    if image_html:
                        placeholder = f'__IMAGE_PLACEHOLDER_{placeholder_counter}__'
                        placeholders[placeholder] = image_html
                        placeholder_counter += 1
                        return placeholder
                except ValueError:
                    pass
            return ''
        
        # Заменяем маркеры на плейсхолдеры
        processed_content = re.sub(marker_pattern, replace_with_placeholder, content, flags=re.IGNORECASE | re.UNICODE)
        
        # Теперь разбиваем на абзацы
        paragraphs = processed_content.split('\n\n')
        
        # Если нет двойных переносов, разбиваем по одинарным
        if len(paragraphs) == 1 and paragraphs[0].strip():
            paragraphs = processed_content.split('\n')
        
        result_parts = []
        for p in paragraphs:
            p = p.strip()
            if not p:
                continue
            
            # Разбиваем абзац на части (текст и плейсхолдеры)
            parts = re.split(r'(__IMAGE_PLACEHOLDER_\d+__)', p)
            
            paragraph_parts = []
            for part in parts:
                if part.startswith('__IMAGE_PLACEHOLDER_') and part.endswith('__'):
                    # Это плейсхолдер - заменяем на HTML изображения
                    if part in placeholders:
                        paragraph_parts.append(placeholders[part])
                else:
                    # Это текст - экранируем
                    if part.strip():
                        escaped = escape(part)
                        escaped = escaped.replace('\n', '<br>')
                        paragraph_parts.append(escaped)
            
            # Если есть части, создаём абзац
            if paragraph_parts:
                # Проверяем, есть ли текст (не только изображения)
                has_text = any(not p.startswith('<div') for p in paragraph_parts)
                if has_text:
                    # Если есть текст, оборачиваем в <p>
                    result_parts.append(f'<p>{"".join(paragraph_parts)}</p>')
                else:
                    # Если только изображения, добавляем без <p>
                    result_parts.extend(paragraph_parts)
        
        return mark_safe(''.join(result_parts))
    
    else:
        # Автоматическая вставка между абзацами на основе поля order
        # Разбиваем текст на абзацы
        paragraphs = content.split('\n\n')
        
        # Если нет двойных переносов, разбиваем по одинарным
        if len(paragraphs) == 1 and paragraphs[0].strip():
            paragraphs = content.split('\n')
        
        # Обрабатываем абзацы
        processed_paragraphs = []
        for p in paragraphs:
            p = p.strip()
            if p:
                escaped = escape(p)
                escaped = escaped.replace('\n', '<br>')
                processed_paragraphs.append(escaped)
        
        paragraphs = processed_paragraphs
        
        if not paragraphs:
            escaped_content = escape(content)
            escaped_content = escaped_content.replace('\n', '<br>')
            if escaped_content.strip():
                return mark_safe(f'<p>{escaped_content}</p>')
            return mark_safe('')
        
        # Собираем результат
        result_parts = []
        
        for i, paragraph in enumerate(paragraphs):
            # Добавляем абзац
            result_parts.append(f'<p>{paragraph}</p>')
            
            # После абзаца вставляем изображения с позицией i
            # order=0 означает "после первого абзаца" (индекс 0)
            if i in images_by_order:
                for img in images_by_order[i]:
                    result_parts.append(get_image_html(img.order))
        
        # Если есть изображения с order >= количества абзацев, вставляем их после последнего
        max_index = len(paragraphs) - 1
        for order in sorted(images_by_order.keys()):
            if order > max_index:
                result_parts.append(get_image_html(order))
        
        return mark_safe(''.join(result_parts))
