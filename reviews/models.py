from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from submissions.models import Submission

User = get_user_model()

class Review(models.Model):
    """
    Модель рецензии статьи.
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
    
    # Оценки (по шкале 1-5)
    originality = models.PositiveSmallIntegerField("Оригинальность", choices=[
        (1, '1 - Низкая'),
        (2, '2 - Ниже среднего'),
        (3, '3 - Средняя'),
        (4, '4 - Выше среднего'),
        (5, '5 - Высокая'),
    ])
    scientific_value = models.PositiveSmallIntegerField("Научная ценность", choices=[
        (1, '1 - Низкая'),
        (2, '2 - Ниже среднего'),
        (3, '3 - Средняя'),
        (4, '4 - Выше среднего'),
        (5, '5 - Высокая'),
    ])
    methodology = models.PositiveSmallIntegerField("Методология", choices=[
        (1, '1 - Слабая'),
        (2, '2 - Ниже среднего'),
        (3, '3 - Средняя'),
        (4, '4 - Выше среднего'),
        (5, '5 - Сильная'),
    ])
    presentation = models.PositiveSmallIntegerField("Презентация", choices=[
        (1, '1 - Плохая'),
        (2, '2 - Ниже среднего'),
        (3, '3 - Средняя'),
        (4, '4 - Выше среднего'),
        (5, '5 - Отличная'),
    ])
    
    # Комментарии
    comments_for_author = models.TextField("Комментарии для автора")
    comments_for_editor = models.TextField("Комментарии для редактора", blank=True)
    
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
    
    # Дополнительные поля
    is_anonymous = models.BooleanField("Анонимная рецензия", default=True)
    conflict_of_interest = models.BooleanField("Конфликт интересов", default=False)
    
    class Meta:
        verbose_name = "Рецензия"
        verbose_name_plural = "Рецензии"
        unique_together = ('submission', 'reviewer')
        ordering = ['-created_at']

    def __str__(self):
        return f"Рецензия {self.submission.title} - {self.reviewer.get_full_name()}"
    
    @property
    def average_score(self):
        """Вычисляет среднюю оценку."""
        scores = [self.originality, self.scientific_value, self.methodology, self.presentation]
        return sum(scores) / len(scores)
    
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
