from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
<<<<<<< HEAD
=======
from django.core.validators import FileExtensionValidator
>>>>>>> bebf4c4 (initial commit)
from submissions.models import Submission

User = get_user_model()

<<<<<<< HEAD
class Review(models.Model):
    """
    Модель рецензии статьи.
=======

class ReviewAssignment(models.Model):
    """
    Назначение рецензента на статью (OJS-style assignment).
    Отдельно от Review для управления процессом назначения.
    """
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name='review_assignments',
        verbose_name="Подача"
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='review_assignments',
        verbose_name="Рецензент"
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='assigned_reviews',
        null=True,
        verbose_name="Назначил"
    )
    
    # Статус назначения
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('accepted', 'Принята'),
        ('declined', 'Отклонена'),
        ('completed', 'Завершена'),
        ('cancelled', 'Отменена'),
    ]
    status = models.CharField("Статус", max_length=15, choices=STATUS_CHOICES, default='pending')
    
    # Даты и дедлайны
    assigned_at = models.DateTimeField("Дата назначения", auto_now_add=True)
    response_due = models.DateTimeField("Срок ответа", null=True, blank=True)
    review_due = models.DateTimeField("Срок рецензии", null=True, blank=True)
    responded_at = models.DateTimeField("Дата ответа", null=True, blank=True)
    
    # Сообщения
    invitation_message = models.TextField("Пригласительное сообщение", blank=True)
    decline_reason = models.TextField("Причина отказа", blank=True)
    
    # Настройки
    can_view_identity = models.BooleanField(
        "Может видеть авторов", 
        default=False,
        help_text="Для открытого рецензирования"
    )
    is_blind = models.BooleanField(
        "Слепое рецензирование",
        default=True,
        help_text="Рецензент не видит авторов"
    )
    
    # Связь с рецензией (после принятия)
    review = models.OneToOneField(
        'Review',
        on_delete=models.SET_NULL,
        related_name='review_assignment',
        null=True,
        blank=True,
        verbose_name="Рецензия"
    )
    
    class Meta:
        verbose_name = "Назначение рецензента"
        verbose_name_plural = "Назначения рецензентов"
        unique_together = ('submission', 'reviewer')
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"Рецензия {self.submission.submission_id} - {self.reviewer.get_full_name()}"
    
    def accept(self):
        """Принимает назначение."""
        from django.utils import timezone
        self.status = 'accepted'
        self.responded_at = timezone.now()
        self.save()
    
    def decline(self, reason=''):
        """Отклоняет назначение."""
        from django.utils import timezone
        self.status = 'declined'
        self.decline_reason = reason
        self.responded_at = timezone.now()
        self.save()
    
    def is_overdue(self):
        """Проверяет, просрочен ли дедлайн."""
        from django.utils import timezone
        if self.review_due and self.status in ['accepted', 'pending']:
            return timezone.now() > self.review_due
        return False

class Review(models.Model):
    """
    Модель рецензии статьи (полный OJS-style review).
>>>>>>> bebf4c4 (initial commit)
    Содержит оценку, комментарии и рекомендации рецензента.
    """
    # Связи
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="Отправка"
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="Рецензент"
    )
    
<<<<<<< HEAD
    # Оценки (по шкале 1-5)
=======
    # Связь с назначением
    assignment = models.OneToOneField(
        'ReviewAssignment',
        on_delete=models.SET_NULL,
        related_name='review_obj',
        null=True,
        blank=True,
        verbose_name="Назначение"
    )
    
    # Оценки (по шкале 1-5, nullable для частичного заполнения)
>>>>>>> bebf4c4 (initial commit)
    originality = models.PositiveSmallIntegerField("Оригинальность", choices=[
        (1, '1 - Низкая'),
        (2, '2 - Ниже среднего'),
        (3, '3 - Средняя'),
        (4, '4 - Выше среднего'),
        (5, '5 - Высокая'),
<<<<<<< HEAD
    ])
=======
    ], null=True, blank=True)
>>>>>>> bebf4c4 (initial commit)
    scientific_value = models.PositiveSmallIntegerField("Научная ценность", choices=[
        (1, '1 - Низкая'),
        (2, '2 - Ниже среднего'),
        (3, '3 - Средняя'),
        (4, '4 - Выше среднего'),
        (5, '5 - Высокая'),
<<<<<<< HEAD
    ])
=======
    ], null=True, blank=True)
>>>>>>> bebf4c4 (initial commit)
    methodology = models.PositiveSmallIntegerField("Методология", choices=[
        (1, '1 - Слабая'),
        (2, '2 - Ниже среднего'),
        (3, '3 - Средняя'),
        (4, '4 - Выше среднего'),
        (5, '5 - Сильная'),
<<<<<<< HEAD
    ])
=======
    ], null=True, blank=True)
>>>>>>> bebf4c4 (initial commit)
    presentation = models.PositiveSmallIntegerField("Презентация", choices=[
        (1, '1 - Плохая'),
        (2, '2 - Ниже среднего'),
        (3, '3 - Средняя'),
        (4, '4 - Выше среднего'),
        (5, '5 - Отличная'),
<<<<<<< HEAD
    ])
    
    # Комментарии
    comments_for_author = models.TextField("Комментарии для автора")
    comments_for_editor = models.TextField("Комментарии для редактора", blank=True)
=======
    ], null=True, blank=True)
    
    # Дополнительные критерии OJS
    language_quality = models.PositiveSmallIntegerField("Качество языка", choices=[
        (1, '1 - Плохое'),
        (2, '2 - Ниже среднего'),
        (3, '3 - Среднее'),
        (4, '4 - Выше среднего'),
        (5, '5 - Отличное'),
    ], null=True, blank=True)
    relevance = models.PositiveSmallIntegerField("Релевантность", choices=[
        (1, '1 - Низкая'),
        (2, '2 - Ниже среднего'),
        (3, '3 - Средняя'),
        (4, '4 - Выше среднего'),
        (5, '5 - Высокая'),
    ], null=True, blank=True)
    
    # Комментарии (расширенные для OJS)
    comments_for_author = models.TextField("Комментарии для автора", blank=True)
    comments_for_editor = models.TextField("Комментарии для редактора", blank=True)
    general_comments = models.TextField("Общие комментарии", blank=True)
    
    # Структурированные комментарии (для удобства авторов)
    strengths = models.TextField("Сильные стороны", blank=True)
    weaknesses = models.TextField("Слабые стороны", blank=True)
    suggestions = models.TextField("Рекомендации по улучшению", blank=True)
>>>>>>> bebf4c4 (initial commit)
    
    # Рекомендация
    RECOMMENDATION_CHOICES = [
        ('accept', 'Принять'),
        ('minor_revision', 'Незначительные исправления'),
        ('major_revision', 'Значительные исправления'),
        ('reject', 'Отклонить'),
    ]
    recommendation = models.CharField(
        "Рекомендация", 
        max_length=20, 
        choices=RECOMMENDATION_CHOICES
    )
    
    # Статус
    STATUS_CHOICES = [
        ('assigned', 'Назначена'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершена'),
    ]
    status = models.CharField("Статус", max_length=15, choices=STATUS_CHOICES, default='assigned')
    
    # Даты
    assigned_at = models.DateTimeField("Дата назначения", auto_now_add=True)
    completed_at = models.DateTimeField("Дата завершения", null=True, blank=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    
<<<<<<< HEAD
    # Дополнительные поля
    is_anonymous = models.BooleanField("Анонимная рецензия", default=True)
    conflict_of_interest = models.BooleanField("Конфликт интересов", default=False)
=======
    # Файлы рецензии
    review_file = models.FileField(
        "Файл рецензии",
        upload_to='reviews/files/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])],
        blank=True,
        null=True
    )
    annotated_manuscript = models.FileField(
        "Аннотированная рукопись",
        upload_to='reviews/annotated/',
        blank=True,
        null=True
    )
    
    # Дополнительные поля OJS
    is_anonymous = models.BooleanField("Анонимная рецензия", default=True)
    conflict_of_interest = models.BooleanField("Конфликт интересов", default=False)
    conflict_details = models.TextField("Детали конфликта интересов", blank=True)
    
    # Время, потраченное на рецензию
    time_spent = models.PositiveIntegerField(
        "Потрачено времени (минуты)",
        null=True,
        blank=True,
        help_text="Сколько времени рецензент потратил на рецензию"
    )
    
    # Видимость для автора
    visible_to_author = models.BooleanField("Видима автору", default=True)
    
    # Версия рецензируемого файла
    reviewed_file_version = models.PositiveIntegerField("Версия рецензируемого файла", default=1)
    
    # История изменений
    revision_requested = models.BooleanField("Требуются исправления", default=False)
    revision_number = models.PositiveIntegerField("Номер ревизии", default=0)
>>>>>>> bebf4c4 (initial commit)
    
    class Meta:
        verbose_name = "Рецензия"
        verbose_name_plural = "Рецензии"
<<<<<<< HEAD
        unique_together = ('submission', 'reviewer')
        ordering = ['-created_at']

    def __str__(self):
        return f"Рецензия {self.submission.title} - {self.reviewer.get_full_name()}"
    
    @property
    def average_score(self):
        """Вычисляет среднюю оценку."""
        scores = [self.originality, self.scientific_value, self.methodology, self.presentation]
        return sum(scores) / len(scores)
=======
        unique_together = ('submission', 'reviewer', 'revision_number')
        ordering = ['-created_at']

    def __str__(self):
        return f"Рецензия {self.submission.submission_id} - {self.reviewer.get_full_name()}"
    
    @property
    def average_score(self):
        """Вычисляет среднюю оценку по всем заполненным критериям."""
        scores = []
        if self.originality:
            scores.append(self.originality)
        if self.scientific_value:
            scores.append(self.scientific_value)
        if self.methodology:
            scores.append(self.methodology)
        if self.presentation:
            scores.append(self.presentation)
        if self.language_quality:
            scores.append(self.language_quality)
        if self.relevance:
            scores.append(self.relevance)
        if scores:
            return sum(scores) / len(scores)
        return None
>>>>>>> bebf4c4 (initial commit)
    
    @property
    def is_completed(self):
        """Проверяет, завершена ли рецензия."""
        return self.status == 'completed'
    
    @property
    def recommendation_display(self):
        """Возвращает рекомендацию на русском языке."""
        recommendation_map = {
            'accept': 'Принять',
            'minor_revision': 'Незначительные исправления',
            'major_revision': 'Значительные исправления',
            'reject': 'Отклонить',
        }
        return recommendation_map.get(self.recommendation, self.recommendation)
    
    def complete_review(self):
        """Отмечает рецензию как завершенную."""
        from django.utils import timezone
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    def get_score_description(self, score):
        """Возвращает описание оценки."""
        descriptions = {
            1: 'Очень слабо',
            2: 'Слабо',
            3: 'Удовлетворительно',
            4: 'Хорошо',
            5: 'Отлично',
        }
        return descriptions.get(score, 'Не оценено')
<<<<<<< HEAD
=======
    
    def is_first_review(self):
        """Проверяет, является ли это первой рецензией для этой подачи."""
        return self.revision_number == 0


class EditorialDecision(models.Model):
    """
    Редакторское решение по статье (OJS-style editorial decision).
    Хранит историю всех решений по статье.
    """
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name='editorial_decisions',
        verbose_name="Подача"
    )
    decision_maker = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='editorial_decisions',
        null=True,
        verbose_name="Принял решение"
    )
    
    # Тип решения
    DECISION_CHOICES = [
        ('accept', 'Принять'),
        ('revision_minor', 'Требуются незначительные исправления'),
        ('revision_major', 'Требуются значительные исправления'),
        ('resubmit', 'Пересмотреть и отправить заново'),
        ('reject', 'Отклонить'),
        ('decline', 'Отозвать'),
    ]
    decision = models.CharField("Решение", max_length=20, choices=DECISION_CHOICES)
    
    # Комментарии
    comments = models.TextField("Комментарии", blank=True)
    comments_for_author = models.TextField("Комментарии для автора", blank=True)
    internal_notes = models.TextField("Внутренние заметки", blank=True)
    
    # Статус
    is_final = models.BooleanField("Финальное решение", default=False)
    
    # Даты
    decided_at = models.DateTimeField("Дата решения", auto_now_add=True)
    
    # Связь с рецензиями
    reviews = models.ManyToManyField(
        Review,
        related_name='decisions',
        blank=True,
        verbose_name="Учтенные рецензии"
    )
    
    class Meta:
        verbose_name = "Редакторское решение"
        verbose_name_plural = "Редакторские решения"
        ordering = ['-decided_at']
    
    def __str__(self):
        return f"{self.get_decision_display()} - {self.submission.submission_id}"
    
    def get_decision_display_ru(self):
        """Возвращает решение на русском языке."""
        decision_map = {
            'accept': 'Принять',
            'revision_minor': 'Требуются незначительные исправления',
            'revision_major': 'Требуются значительные исправления',
            'resubmit': 'Пересмотреть и отправить заново',
            'reject': 'Отклонить',
            'decline': 'Отозвать',
        }
        return decision_map.get(self.decision, self.decision)
>>>>>>> bebf4c4 (initial commit)
