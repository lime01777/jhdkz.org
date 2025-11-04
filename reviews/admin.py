from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Review, ReviewAssignment, EditorialDecision

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Админка для модели рецензии."""
    
    list_display = ('submission', 'reviewer', 'status', 'average_score', 'recommendation', 'assigned_at')
    list_filter = ('status', 'recommendation', 'is_anonymous', 'conflict_of_interest', 'assigned_at')
    search_fields = ('submission__title', 'reviewer__full_name', 'reviewer__username')
    ordering = ('-assigned_at',)
    
    # Поля только для чтения
    readonly_fields = ('assigned_at', 'created_at', 'updated_at')
    
    # Действия
    actions = ['assign_reviews', 'complete_reviews', 'mark_conflict_of_interest']
    
    def assign_reviews(self, request, queryset):
        """Назначить рецензии."""
        updated = queryset.update(status='assigned')
        self.message_user(request, f'{updated} рецензий назначено.')
    assign_reviews.short_description = "Назначить рецензии"
    
    def complete_reviews(self, request, queryset):
        """Завершить рецензии."""
        from django.utils import timezone
        updated = queryset.update(status='completed', completed_at=timezone.now())
        self.message_user(request, f'{updated} рецензий завершено.')
    complete_reviews.short_description = "Завершить рецензии"
    
    def mark_conflict_of_interest(self, request, queryset):
        """Отметить конфликт интересов."""
        updated = queryset.update(conflict_of_interest=True)
        self.message_user(request, f'Конфликт интересов отмечен для {updated} рецензий.')
    mark_conflict_of_interest.short_description = "Отметить конфликт интересов"
    
    def average_score(self, obj):
        """Средняя оценка."""
        avg = obj.average_score
        return f"{avg:.1f}" if avg else "N/A"
    average_score.short_description = "Средняя оценка"
    
    def get_queryset(self, request):
        """Оптимизированный запрос с select_related."""
        return super().get_queryset(request).select_related('submission', 'reviewer', 'assignment')
    
    # Обновленные поля для OJS
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('submission', 'reviewer', 'assignment', 'status', 'recommendation', 'revision_number')
        }),
        (_('Оценки'), {
            'fields': ('originality', 'scientific_value', 'methodology', 'presentation', 'language_quality', 'relevance')
        }),
        (_('Комментарии'), {
            'fields': ('comments_for_author', 'comments_for_editor', 'general_comments', 
                      'strengths', 'weaknesses', 'suggestions')
        }),
        (_('Файлы'), {
            'fields': ('review_file', 'annotated_manuscript', 'reviewed_file_version')
        }),
        (_('Настройки'), {
            'fields': ('is_anonymous', 'conflict_of_interest', 'conflict_details', 
                      'visible_to_author', 'time_spent', 'revision_requested')
        }),
        (_('Даты'), {
            'fields': ('assigned_at', 'completed_at', 'created_at', 'updated_at')
        }),
    )


@admin.register(ReviewAssignment)
class ReviewAssignmentAdmin(admin.ModelAdmin):
    """Админка для назначения рецензентов."""
    
    list_display = ('submission', 'reviewer', 'status', 'assigned_at', 'review_due', 'is_overdue')
    list_filter = ('status', 'is_blind', 'can_view_identity', 'assigned_at')
    search_fields = ('submission__submission_id', 'submission__title_ru', 'reviewer__full_name', 'reviewer__username')
    ordering = ('-assigned_at',)
    
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('submission', 'reviewer', 'assigned_by', 'status')
        }),
        (_('Дедлайны'), {
            'fields': ('response_due', 'review_due', 'responded_at')
        }),
        (_('Сообщения'), {
            'fields': ('invitation_message', 'decline_reason')
        }),
        (_('Настройки'), {
            'fields': ('is_blind', 'can_view_identity')
        }),
        (_('Рецензия'), {
            'fields': ('review',)
        }),
    )
    
    readonly_fields = ('assigned_at', 'responded_at')
    
    def is_overdue(self, obj):
        """Проверяет просрочку дедлайна."""
        return obj.is_overdue()
    is_overdue.boolean = True
    is_overdue.short_description = "Просрочено"


@admin.register(EditorialDecision)
class EditorialDecisionAdmin(admin.ModelAdmin):
    """Админка для редакторских решений."""
    
    list_display = ('submission', 'decision', 'decision_maker', 'decided_at', 'is_final')
    list_filter = ('decision', 'is_final', 'decided_at')
    search_fields = ('submission__submission_id', 'submission__title_ru', 'decision_maker__full_name')
    ordering = ('-decided_at',)
    
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('submission', 'decision_maker', 'decision', 'is_final')
        }),
        (_('Комментарии'), {
            'fields': ('comments', 'comments_for_author', 'internal_notes')
        }),
        (_('Рецензии'), {
            'fields': ('reviews',)
        }),
        (_('Дата'), {
            'fields': ('decided_at',)
        }),
    )
    
    readonly_fields = ('decided_at',)
    filter_horizontal = ('reviews',)
    
    def get_decision_display_ru(self, obj):
        """Отображение решения на русском."""
        return obj.get_decision_display_ru()
    get_decision_display_ru.short_description = "Решение"
