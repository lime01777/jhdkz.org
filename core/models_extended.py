"""
Дополнительные модели для core: локализации новостей и страниц, события, сырые документы.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from .models import News, Page


# Используем JSONField из правильного места в зависимости от версии Django
# Django 3.1+ использует models.JSONField
JSONField = models.JSONField


class NewsLocale(models.Model):
    """
    Локализованное содержимое новости.
    """
    news = models.ForeignKey(
        News,
        on_delete=models.CASCADE,
        related_name='locales',
        verbose_name="Новость"
    )
    language = models.CharField(
        "Язык",
        max_length=2,
        choices=[
            ('ru', 'Русский'),
            ('kk', 'Казахский'),
            ('en', 'Английский'),
        ],
        db_index=True
    )
    title = models.CharField("Заголовок", max_length=200)
    body_html = models.TextField("Полный текст (HTML)")
    
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    
    class Meta:
        verbose_name = "Локализация новости"
        verbose_name_plural = "Локализации новостей"
        unique_together = ('news', 'language')
    
    def __str__(self):
        return f"{self.news.title} ({self.language})"


class PageLocale(models.Model):
    """
    Локализованное содержимое страницы.
    """
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name='locales',
        verbose_name="Страница"
    )
    language = models.CharField(
        "Язык",
        max_length=2,
        choices=[
            ('ru', 'Русский'),
            ('kk', 'Казахский'),
            ('en', 'Английский'),
        ],
        db_index=True
    )
    title = models.CharField("Заголовок", max_length=200)
    body_html = models.TextField("Полный текст (HTML)")
    
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    
    class Meta:
        verbose_name = "Локализация страницы"
        verbose_name_plural = "Локализации страниц"
        unique_together = ('page', 'language')
    
    def __str__(self):
        return f"{self.page.title} ({self.language})"


class Event(models.Model):
    """
    События для логирования просмотров, загрузок и т.д.
    """
    object_type = models.CharField(
        "Тип объекта",
        max_length=20,
        choices=[
            ('article', 'Статья'),
            ('file', 'Файл'),
            ('issue', 'Выпуск'),
            ('news', 'Новость'),
        ],
        db_index=True
    )
    object_id = models.PositiveIntegerField("ID объекта", db_index=True)
    kind = models.CharField(
        "Тип события",
        max_length=20,
        choices=[
            ('view', 'Просмотр'),
            ('download', 'Загрузка'),
            ('redirect', 'Редирект'),
        ],
        db_index=True
    )
    ip = models.GenericIPAddressField("IP адрес", null=True, blank=True)
    user_agent = models.CharField("User Agent", max_length=500, blank=True)
    referer = models.URLField("Referer", max_length=500, blank=True)
    timestamp = models.DateTimeField("Время", auto_now_add=True, db_index=True)
    
    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "События"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['object_type', 'object_id', 'kind']),
            models.Index(fields=['timestamp', 'kind']),
        ]
    
    def __str__(self):
        return f"{self.kind} {self.object_type}:{self.object_id} at {self.timestamp}"


class RawDocument(models.Model):
    """
    Сырые документы, полученные при ETL процессе.
    Используется для дедупликации и отслеживания источников.
    """
    source_url = models.URLField("URL источника", max_length=1000, db_index=True)
    sha256 = models.CharField("SHA256 хеш", max_length=64, unique=True, db_index=True)
    data = JSONField("Данные (JSON)", default=dict)
    fetched_at = models.DateTimeField("Дата получения", auto_now_add=True, db_index=True)
    
    class Meta:
        verbose_name = "Сырой документ"
        verbose_name_plural = "Сырые документы"
        ordering = ['-fetched_at']
        indexes = [
            models.Index(fields=['sha256']),
            models.Index(fields=['source_url', 'fetched_at']),
        ]
    
    def __str__(self):
        return f"{self.source_url} ({self.sha256[:16]}...)"


class Affiliation(models.Model):
    """
    Аффилиации авторов (организации, университеты и т.д.).
    """
    name = models.CharField("Название", max_length=500, db_index=True)
    name_en = models.CharField("Название (англ.)", max_length=500, blank=True)
    country = models.CharField("Страна", max_length=100, blank=True, db_index=True)
    city = models.CharField("Город", max_length=100, blank=True)
    
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    
    class Meta:
        verbose_name = "Аффилиация"
        verbose_name_plural = "Аффилиации"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['country']),
        ]
    
    def __str__(self):
        if self.country:
            return f"{self.name}, {self.country}"
        return self.name

