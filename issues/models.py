from django.db import models
from django.utils.translation import gettext_lazy as _

class Issue(models.Model):
    """
    Модель выпуска журнала.
    Содержит информацию о номере, годе, дате публикации и файлах.
    """
    # Основная информация
    year = models.PositiveIntegerField("Год", help_text="Год выпуска журнала")
    number = models.PositiveIntegerField("Номер", help_text="Номер выпуска в году")
    
    # Многоязычные поля
    title_ru = models.CharField("Название (русский)", max_length=255)
    title_kk = models.CharField("Название (казахский)", max_length=255, blank=True)
    title_en = models.CharField("Название (английский)", max_length=255, blank=True)
    
    # Даты
    published_at = models.DateField("Дата публикации", null=True, blank=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    
    # Файлы
    cover_image = models.ImageField("Обложка", upload_to='issues/covers/', blank=True, null=True)
    pdf_file = models.FileField("PDF выпуска", upload_to='issues/pdfs/', blank=True, null=True)
    
    # Статус
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('published', 'Опубликован'),
        ('archived', 'Архивирован'),
    ]
    status = models.CharField("Статус", max_length=10, choices=STATUS_CHOICES, default='draft')
    
    # Метаданные
    description = models.TextField("Описание", blank=True)
    keywords = models.CharField("Ключевые слова", max_length=500, blank=True)
    
    class Meta:
        verbose_name = "Выпуск"
        verbose_name_plural = "Выпуски"
        unique_together = ('year', 'number')
        ordering = ['-year', '-number']

    def __str__(self):
        return f"Выпуск {self.year} №{self.number}"
    
    def get_title(self, language='ru'):
        """Возвращает название на указанном языке."""
        title_map = {
            'ru': self.title_ru,
            'kk': self.title_kk,
            'en': self.title_en,
        }
        return title_map.get(language, self.title_ru)
    
    @property
    def is_published(self):
        """Проверяет, опубликован ли выпуск."""
        return self.status == 'published'
    
    @property
    def articles_count(self):
        """Возвращает количество статей в выпуске."""
        return self.articles.count()
    
    def get_volume_info(self):
        """Возвращает информацию о томе и номере."""
        return f"Volume {self.year}, Number {self.number}"
