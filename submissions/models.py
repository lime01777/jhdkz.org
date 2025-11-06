from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator

User = get_user_model()

class Section(models.Model):
    """
    Раздел журнала (Research Articles, Reviews, Case Studies и т.д.)
    """
    title_ru = models.CharField("Название (русский)", max_length=200)
    title_kk = models.CharField("Название (казахский)", max_length=200, blank=True)
    title_en = models.CharField("Название (английский)", max_length=200, blank=True)
    slug = models.SlugField("URL", unique=True)
    description = models.TextField("Описание", blank=True)
    is_active = models.BooleanField("Активен", default=True)
    order = models.PositiveIntegerField("Порядок", default=0)
    
    # Политики рецензирования
    require_review = models.BooleanField("Требуется рецензирование", default=True)
    review_type = models.CharField("Тип рецензирования", max_length=20, choices=[
        ('single', 'Одно рецензирование'),
        ('double', 'Двойное слепое'),
        ('open', 'Открытое'),
    ], default='double')
    
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    
    class Meta:
        verbose_name = "Раздел"
        verbose_name_plural = "Разделы"
        ordering = ['order', 'title_ru']
    
    def __str__(self):
        return self.title_ru


class Submission(models.Model):
    """
    Модель отправки статьи (полный OJS workflow).
    Управляет процессом подачи и рецензирования статей.
    """
    # Основная информация
    title_ru = models.CharField("Название статьи (русский)", max_length=500, blank=True, default='')
    title_kk = models.CharField("Название статьи (казахский)", max_length=500, blank=True)
    title_en = models.CharField("Название статьи (английский)", max_length=500, blank=True)
    
    abstract_ru = models.TextField("Аннотация (русский)", blank=True, default='')
    abstract_kk = models.TextField("Аннотация (казахский)", blank=True)
    abstract_en = models.TextField("Аннотация (английский)", blank=True)
    
    keywords_ru = models.CharField("Ключевые слова (русский)", max_length=500, blank=True, default='')
    keywords_kk = models.CharField("Ключевые слова (казахский)", max_length=500, blank=True)
    keywords_en = models.CharField("Ключевые слова (английский)", max_length=500, blank=True)
    
    # Раздел
    section = models.ForeignKey(
        'Section',
        on_delete=models.PROTECT,
        related_name='submissions',
        verbose_name="Раздел",
        null=True,
        blank=True
    )
    
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
    
    # Файлы - OJS поддерживает несколько версий
    manuscript_file = models.FileField(
        "Рукопись", 
        upload_to='submissions/manuscripts/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])],
        help_text="Основной файл рукописи (PDF, DOC, DOCX)"
    )
    
    # Дополнительные файлы через отдельную модель
    
    # Статус и workflow (полный OJS workflow)
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('submitted', 'Отправлена редактору'),
        ('reviewing', 'На рецензии'),
        ('in_editing', 'В редактировании'),
        ('reviewer_assigned', 'Рецензент назначен'),
        ('review_completed', 'Рецензия завершена'),
        ('revision_requested', 'Требуются исправления'),
        ('revision_submitted', 'Исправления отправлены'),
        ('accepted', 'Принята'),
        ('rejected', 'Отклонена'),
        ('in_production', 'В производстве'),
        ('scheduled', 'Запланирована к публикации'),
        ('published', 'Опубликована'),
        ('declined', 'Отозвана автором'),
    ]
    status = models.CharField("Статус", max_length=25, choices=STATUS_CHOICES, default='draft')
    
    # Редактор, назначенный к статье
    assigned_editor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='assigned_submissions',
        verbose_name="Назначенный редактор",
        null=True,
        blank=True
    )
    
    # Тип рецензирования
    review_type = models.CharField("Тип рецензирования", max_length=20, choices=[
        ('single', 'Одно рецензирование'),
        ('double', 'Двойное слепое'),
        ('open', 'Открытое'),
    ], default='double')
    
    # Даты
    submitted_at = models.DateTimeField("Дата отправки", null=True, blank=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    
    # Комментарии на разных этапах
    author_comments = models.TextField("Комментарии автора редактору", blank=True)
    editor_comments = models.TextField("Комментарии редактора автору", blank=True)
    editor_reviewer_comments = models.TextField("Комментарии редактора рецензенту", blank=True)
    
    # Дополнительные поля OJS
    # Исследовательская информация
    research_field = models.CharField("Область исследования", max_length=200, blank=True)
    methodology = models.TextField("Методология", blank=True)
    funding = models.CharField("Финансирование", max_length=500, blank=True)
    
    # Этические аспекты
    ethics_approval = models.BooleanField("Получено этическое одобрение", default=False)
    ethics_committee = models.CharField("Этический комитет", max_length=200, blank=True)
    conflict_of_interest = models.TextField("Конфликт интересов", blank=True)
    data_availability = models.TextField("Доступность данных", blank=True)
    
    # Подача
    submission_type = models.CharField("Тип подачи", max_length=20, choices=[
        ('new', 'Новая статья'),
        ('revision', 'Исправленная версия'),
        ('resubmission', 'Повторная подача'),
    ], default='new')
    
    # Связь с оригинальной подачей (для ревизий)
    parent_submission = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        related_name='revisions',
        verbose_name="Родительская подача",
        null=True,
        blank=True
    )
    
    # Техническая информация
    submission_id = models.CharField("ID отправки", max_length=20, unique=True, blank=True)
    language = models.CharField("Язык", max_length=2, default='ru', choices=[
        ('ru', 'Русский'),
        ('kk', 'Казахский'),
        ('en', 'Английский'),
    ])
    
    # Дополнительные даты OJS
    last_review_date = models.DateTimeField("Дата последней рецензии", null=True, blank=True)
    last_revision_date = models.DateTimeField("Дата последних исправлений", null=True, blank=True)
    editor_decision_date = models.DateTimeField("Дата решения редактора", null=True, blank=True)
    
    class Meta:
        verbose_name = "Отправка"
        verbose_name_plural = "Отправки"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_title('ru')} - {self.corresponding_author.get_full_name()}"
    
    def save(self, *args, **kwargs):
        """Генерирует уникальный ID отправки при создании."""
        if not self.submission_id:
            import uuid
            self.submission_id = f"SUB{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def is_submitted(self):
        """Проверяет, отправлена ли статья."""
        return self.status in ['submitted', 'reviewing', 'revision_requested', 'accepted', 'published']
    
    @property
    def is_under_review(self):
        """Проверяет, находится ли статья на рецензии."""
        return self.status in ['reviewing', 'reviewer_assigned']
    
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
    
    def get_title(self, language='ru'):
        """Возвращает название на указанном языке."""
        title_map = {
            'ru': self.title_ru,
            'kk': self.title_kk,
            'en': self.title_en,
        }
        return title_map.get(language, self.title_ru) or self.title_ru
    
    def get_abstract(self, language='ru'):
        """Возвращает аннотацию на указанном языке."""
        abstract_map = {
            'ru': self.abstract_ru,
            'kk': self.abstract_kk,
            'en': self.abstract_en,
        }
        return abstract_map.get(language, self.abstract_ru) or self.abstract_ru
    
    def get_keywords(self, language='ru'):
        """Возвращает ключевые слова на указанном языке."""
        keywords_map = {
            'ru': self.keywords_ru,
            'kk': self.keywords_kk,
            'en': self.keywords_en,
        }
        return keywords_map.get(language, self.keywords_ru) or self.keywords_ru
    
    def get_status_display_ru(self):
        """Возвращает статус на русском языке."""
        status_map = {
            'draft': 'Черновик',
            'submitted': 'Отправлена редактору',
            'reviewing': 'На рецензии',
            'in_editing': 'В редактировании',
            'reviewer_assigned': 'Рецензент назначен',
            'review_completed': 'Рецензия завершена',
            'revision_requested': 'Требуются исправления',
            'revision_submitted': 'Исправления отправлены',
            'accepted': 'Принята',
            'rejected': 'Отклонена',
            'in_production': 'В производстве',
            'scheduled': 'Запланирована к публикации',
            'published': 'Опубликована',
            'declined': 'Отозвана автором',
        }
        return status_map.get(self.status, self.status)
    
    @property
    def current_step(self):
        """Определяет текущий шаг в процессе подачи."""
        step_map = {
            'draft': 1,
            'submitted': 2,
            'reviewing': 3,
            'reviewer_assigned': 3,
            'review_completed': 4,
            'revision_requested': 5,
            'revision_submitted': 3,
            'accepted': 6,
            'rejected': 0,
            'in_production': 7,
            'scheduled': 8,
            'published': 9,
            'declined': 0,
        }
        return step_map.get(self.status, 0)
    
    def can_be_submitted(self):
        """Проверяет, можно ли отправить статью."""
        return (
            self.status == 'draft' and
            self.title_ru and
            self.abstract_ru and
            self.manuscript_file and
            self.section
        )


class SubmissionFile(models.Model):
    """
    Файлы, прикрепленные к подаче (поддержка нескольких файлов как в OJS).
    """
    FILE_TYPE_CHOICES = [
        ('manuscript', 'Рукопись'),
        ('supplementary', 'Дополнительный файл'),
        ('data', 'Данные'),
        ('figure', 'Рисунок'),
        ('table', 'Таблица'),
        ('other', 'Другое'),
    ]
    
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name="Подача"
    )
    file = models.FileField(
        "Файл",
        upload_to='submissions/files/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'zip', 'jpg', 'png'])],
    )
    file_type = models.CharField("Тип файла", max_length=20, choices=FILE_TYPE_CHOICES, default='manuscript')
    name = models.CharField("Название файла", max_length=255, blank=True)
    description = models.TextField("Описание", blank=True)
    
    # Версия файла (для ревизий)
    version = models.PositiveIntegerField("Версия", default=1)
    
    uploaded_at = models.DateTimeField("Дата загрузки", auto_now_add=True)
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='uploaded_files',
        null=True,
        verbose_name="Загрузил"
    )
    
    class Meta:
        verbose_name = "Файл подачи"
        verbose_name_plural = "Файлы подачи"
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.submission.submission_id} - {self.name or self.file.name}"


class SubmissionAuthor(models.Model):
    """
    Дополнительная информация об авторах (более детальная, чем просто ManyToMany).
    """
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name='submission_authors'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='submission_authorships'
    )
    
    # Порядок авторов
    author_order = models.PositiveIntegerField("Порядок", default=1)
    
    # Роль автора
    is_corresponding = models.BooleanField("Корреспондирующий автор", default=False)
    is_principal = models.BooleanField("Главный автор", default=False)
    
    # Дополнительная информация
    affiliation = models.CharField("Аффилиация", max_length=500, blank=True)
    orcid = models.CharField("ORCID", max_length=19, blank=True)
    email = models.EmailField("Email", blank=True)
    
    class Meta:
        verbose_name = "Автор подачи"
        verbose_name_plural = "Авторы подачи"
        unique_together = ('submission', 'author')
        ordering = ['author_order']
    
    def __str__(self):
        role = " (корреспондирующий)" if self.is_corresponding else ""
        return f"{self.author.get_full_name()}{role}"
