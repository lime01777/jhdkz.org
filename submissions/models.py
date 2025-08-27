from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Submission(models.Model):
    """
    Модель отправки статьи.
    Управляет процессом подачи и рецензирования статей.
    """
    # Основная информация
    title = models.CharField("Название статьи", max_length=500)
    abstract = models.TextField("Аннотация")
    keywords = models.CharField("Ключевые слова", max_length=500)
    
    # Авторы
    corresponding_author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='submissions_as_corresponding',
        verbose_name="Корреспондирующий автор"
    )
    co_authors = models.ManyToManyField(
        User,
        related_name='submissions_as_coauthor',
        verbose_name="Соавторы",
        blank=True
    )
    
    # Файлы
    manuscript_file = models.FileField("Рукопись", upload_to='submissions/manuscripts/')
    supplementary_files = models.FileField(
        "Дополнительные файлы", 
        upload_to='submissions/supplementary/',
        blank=True,
        null=True
    )
    
    # Статус и workflow
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('submitted', 'Отправлена'),
        ('under_review', 'На рецензии'),
        ('revision_requested', 'Требуются исправления'),
        ('accepted', 'Принята'),
        ('rejected', 'Отклонена'),
        ('published', 'Опубликована'),
    ]
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Даты
    submitted_at = models.DateTimeField("Дата отправки", null=True, blank=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    
    # Комментарии
    author_comments = models.TextField("Комментарии автора", blank=True)
    editor_comments = models.TextField("Комментарии редактора", blank=True)
    
    # Техническая информация
    submission_id = models.CharField("ID отправки", max_length=20, unique=True, blank=True)
    language = models.CharField("Язык", max_length=2, default='ru', choices=[
        ('ru', 'Русский'),
        ('kk', 'Казахский'),
        ('en', 'Английский'),
    ])
    
    class Meta:
        verbose_name = "Отправка"
        verbose_name_plural = "Отправки"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.corresponding_author.get_full_name()}"
    
    def save(self, *args, **kwargs):
        """Генерирует уникальный ID отправки при создании."""
        if not self.submission_id:
            import uuid
            self.submission_id = f"SUB{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def is_submitted(self):
        """Проверяет, отправлена ли статья."""
        return self.status in ['submitted', 'under_review', 'revision_requested', 'accepted', 'published']
    
    @property
    def is_under_review(self):
        """Проверяет, находится ли статья на рецензии."""
        return self.status == 'under_review'
    
    @property
    def is_accepted(self):
        """Проверяет, принята ли статья."""
        return self.status in ['accepted', 'published']
    
    @property
    def is_rejected(self):
        """Проверяет, отклонена ли статья."""
        return self.status == 'rejected'
    
    def get_authors_list(self):
        """Возвращает список всех авторов."""
        authors = [self.corresponding_author]
        authors.extend(self.co_authors.all())
        return authors
    
    def get_status_display_ru(self):
        """Возвращает статус на русском языке."""
        status_map = {
            'draft': 'Черновик',
            'submitted': 'Отправлена',
            'under_review': 'На рецензии',
            'revision_requested': 'Требуются исправления',
            'accepted': 'Принята',
            'rejected': 'Отклонена',
            'published': 'Опубликована',
        }
        return status_map.get(self.status, self.status)
