"""
Дополнительные модели для статей: локализации, ключевые слова, файлы.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.indexes import GinIndex
from .models import Article


class ArticleLocale(models.Model):
    """
    Локализованное содержимое статьи (полный текст HTML).
    """
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='locales',
        verbose_name="Статья"
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
    title = models.CharField("Заголовок", max_length=500)
    abstract = models.TextField("Аннотация")
    body_html = models.TextField("Полный текст (HTML)", blank=True)
    
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    
    class Meta:
        verbose_name = "Локализация статьи"
        verbose_name_plural = "Локализации статей"
        unique_together = ('article', 'language')
        indexes = [
            # GIN индекс для полнотекстового поиска (Postgres)
            GinIndex(
                fields=['title', 'abstract', 'body_html'],
                name='article_locale_gin_idx',
                opclasses=['gin_trgm_ops', 'gin_trgm_ops', 'gin_trgm_ops'],
            ) if hasattr(models, 'Index') else models.Index(fields=['title', 'abstract']),
        ]
    
    def __str__(self):
        return f"{self.article.title_ru} ({self.language})"


class Keyword(models.Model):
    """
    Ключевые слова для статей.
    """
    term = models.CharField("Термин", max_length=200, db_index=True)
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
    articles = models.ManyToManyField(
        Article,
        related_name='keywords',
        verbose_name="Статьи",
        blank=True
    )
    
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    
    class Meta:
        verbose_name = "Ключевое слово"
        verbose_name_plural = "Ключевые слова"
        unique_together = ('term', 'language')
        indexes = [
            models.Index(fields=['term', 'language']),
            # GIN индекс для поиска (Postgres)
            GinIndex(
                fields=['term'],
                name='keyword_term_gin_idx',
                opclasses=['gin_trgm_ops'],
            ) if hasattr(models, 'Index') else models.Index(fields=['term']),
        ]
    
    def __str__(self):
        return f"{self.term} ({self.language})"


class ArticleFile(models.Model):
    """
    Файлы, связанные со статьей (PDF, изображения, дополнительные материалы).
    """
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name="Статья"
    )
    kind = models.CharField(
        "Тип файла",
        max_length=20,
        choices=[
            ('pdf', 'PDF'),
            ('image', 'Изображение'),
            ('supp', 'Дополнительные материалы'),
            ('other', 'Другое'),
        ],
        default='pdf',
        db_index=True
    )
    file = models.FileField(
        "Файл",
        upload_to='articles/files/%Y/%m/%d/',
        max_length=500
    )
    original_name = models.CharField("Оригинальное имя", max_length=255)
    content_type = models.CharField("MIME тип", max_length=100, blank=True)
    size = models.PositiveIntegerField("Размер (байт)", default=0)
    description = models.TextField("Описание", blank=True)
    
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    
    class Meta:
        verbose_name = "Файл статьи"
        verbose_name_plural = "Файлы статей"
        ordering = ['kind', 'created_at']
        indexes = [
            models.Index(fields=['article', 'kind']),
        ]
    
    def __str__(self):
        return f"{self.article.title_ru} - {self.original_name}"
    
    def get_absolute_url(self):
        """Возвращает URL для скачивания файла."""
        return reverse('core:file_download', kwargs={'pk': self.pk})

