from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from issues.models import Issue

User = get_user_model()

class Article(models.Model):
    """
    Модель статьи журнала.
    Содержит информацию о статье, авторах, файлах и статистике.
    """
    # Связи
    issue = models.ForeignKey(
        Issue, 
        on_delete=models.CASCADE, 
        related_name='articles', 
        verbose_name="Выпуск"
    )
    authors = models.ManyToManyField(
        User, 
        related_name='articles', 
        verbose_name="Авторы"
    )
    
    # Многоязычные поля
    title_ru = models.CharField("Название (русский)", max_length=500)
    title_kk = models.CharField("Название (казахский)", max_length=500, blank=True)
    title_en = models.CharField("Название (английский)", max_length=500, blank=True)
    
    abstract_ru = models.TextField("Аннотация (русский)")
    abstract_kk = models.TextField("Аннотация (казахский)", blank=True)
    abstract_en = models.TextField("Аннотация (английский)", blank=True)
    
    keywords_ru = models.CharField("Ключевые слова (русский)", max_length=500)
    keywords_kk = models.CharField("Ключевые слова (казахский)", max_length=500, blank=True)
    keywords_en = models.CharField("Ключевые слова (английский)", max_length=500, blank=True)
    
    # Техническая информация
    page_start = models.PositiveIntegerField("Страница начала")
    page_end = models.PositiveIntegerField("Страница конца")
    
    # Файлы
    pdf_file = models.FileField("PDF статьи", upload_to='articles/pdfs/')
    
    # Статус
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('submitted', 'Отправлена'),
        ('review', 'На рецензии'),
        ('accepted', 'Принята'),
        ('rejected', 'Отклонена'),
        ('published', 'Опубликована'),
    ]
    status = models.CharField("Статус", max_length=10, choices=STATUS_CHOICES, default='draft')
    
    # Статистика
    views = models.PositiveIntegerField("Просмотры", default=0)
    downloads = models.PositiveIntegerField("Загрузки", default=0)
    
    # Даты
    submitted_at = models.DateTimeField("Дата отправки", null=True, blank=True)
    published_at = models.DateTimeField("Дата публикации", null=True, blank=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    
    # Дополнительные поля
    doi = models.CharField("DOI", max_length=100, blank=True)
    language = models.CharField("Язык", max_length=2, default='ru', choices=[
        ('ru', 'Русский'),
        ('kk', 'Казахский'),
        ('en', 'Английский'),
    ])
    
    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"
        ordering = ['-created_at']

    def __str__(self):
        return self.title_ru
    
    def get_title(self, language='ru'):
        """Возвращает название на указанном языке."""
        title_map = {
            'ru': self.title_ru,
            'kk': self.title_kk,
            'en': self.title_en,
        }
        return title_map.get(language, self.title_ru)
    
    def get_abstract(self, language='ru'):
        """Возвращает аннотацию на указанном языке."""
        abstract_map = {
            'ru': self.abstract_ru,
            'kk': self.abstract_kk,
            'en': self.abstract_en,
        }
        return abstract_map.get(language, self.abstract_ru)
    
    def get_keywords(self, language='ru'):
        """Возвращает ключевые слова на указанном языке."""
        keywords_map = {
            'ru': self.keywords_ru,
            'kk': self.keywords_kk,
            'en': self.keywords_en,
        }
        return keywords_map.get(language, self.keywords_ru)
    
    @property
    def is_published(self):
        """Проверяет, опубликована ли статья."""
        return self.status == 'published'
    
    @property
    def authors_list(self):
        """Возвращает список авторов в виде строки."""
        return ', '.join([author.get_full_name() for author in self.authors.all()])
    
    def increment_views(self):
        """Увеличивает счетчик просмотров."""
        self.views += 1
        self.save(update_fields=['views'])
    
    def increment_downloads(self):
        """Увеличивает счетчик загрузок."""
        self.downloads += 1
        self.save(update_fields=['downloads'])
    
    def get_pages_info(self):
        """Возвращает информацию о страницах."""
        return f"{self.page_start}-{self.page_end}"
