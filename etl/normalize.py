"""
Нормализация HTML контента.
Удаляет опасные теги и атрибуты, оставляет только белый список.
"""
import re
import logging
from typing import Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup, Tag, NavigableString

logger = logging.getLogger('etl')


# Белый список разрешенных тегов
ALLOWED_TAGS = {
    'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'dl', 'dt', 'dd',
    'a', 'strong', 'em', 'b', 'i', 'u',
    'br', 'hr', 'blockquote', 'pre', 'code',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'img', 'sup', 'sub', 'span', 'div',
}

# Белый список разрешенных атрибутов
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
    'table': ['class'],
    'th': ['scope', 'colspan', 'rowspan'],
    'td': ['colspan', 'rowspan'],
    'div': ['class'],
    'span': ['class'],
    'p': ['class'],
}


def clean_html(html: str, base_url: Optional[str] = None) -> str:
    """
    Очищает HTML от опасных тегов и атрибутов.
    
    Args:
        html: HTML строка для очистки
        base_url: Базовый URL для нормализации относительных ссылок
    
    Returns:
        Очищенный HTML
    """
    if not html:
        return ''
    
    try:
        soup = BeautifulSoup(html, 'lxml')
    except Exception as e:
        logger.warning(f"Ошибка парсинга HTML: {e}")
        # Пытаемся использовать html5lib как fallback
        soup = BeautifulSoup(html, 'html.parser')
    
    # Удаляем скрипты и стили
    for tag in soup(['script', 'style', 'iframe', 'object', 'embed']):
        tag.decompose()
    
    # Очищаем теги
    cleaned = _clean_tag(soup, base_url)
    
    # Убираем множественные пробелы
    result = re.sub(r'\s+', ' ', str(cleaned))
    result = re.sub(r'\n\s*\n', '\n\n', result)
    
    return result.strip()


def _clean_tag(tag: Tag, base_url: Optional[str] = None) -> Tag:
    """Рекурсивно очищает теги."""
    if isinstance(tag, NavigableString):
        return tag
    
    if tag.name not in ALLOWED_TAGS:
        # Заменяем неразрешенный тег на его содержимое
        tag.replace_with(tag.get_text())
        return tag
    
    # Удаляем неразрешенные атрибуты
    allowed_attrs = ALLOWED_ATTRIBUTES.get(tag.name, [])
    attrs_to_remove = []
    for attr in tag.attrs:
        if attr not in allowed_attrs:
            attrs_to_remove.append(attr)
    
    for attr in attrs_to_remove:
        del tag.attrs[attr]
    
    # Нормализуем ссылки
    if tag.name == 'a' and 'href' in tag.attrs:
        href = tag.attrs['href']
        if base_url and not href.startswith(('http://', 'https://')):
            tag.attrs['href'] = urljoin(base_url, href)
    
    # Нормализуем изображения
    if tag.name == 'img' and 'src' in tag.attrs:
        src = tag.attrs['src']
        if base_url and not src.startswith(('http://', 'https://', 'data:')):
            tag.attrs['src'] = urljoin(base_url, src)
    
    # Рекурсивно обрабатываем дочерние элементы
    for child in list(tag.children):
        _clean_tag(child, base_url)
    
    return tag


def extract_text(html: str, max_length: Optional[int] = None) -> str:
    """Извлекает текст из HTML для использования в сниппетах."""
    soup = BeautifulSoup(html, 'lxml')
    text = soup.get_text(separator=' ', strip=True)
    
    if max_length:
        if len(text) > max_length:
            text = text[:max_length].rsplit(' ', 1)[0] + '...'
    
    return text


def normalize_media_url(url: str, base_url: str) -> str:
    """Нормализует URL медиа-файлов."""
    from urllib.parse import urljoin
    if not url.startswith(('http://', 'https://', 'data:')):
        return urljoin(base_url, url)
    return url

