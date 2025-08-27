from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Админка для модели рецензии."""
    
    list_display = ('submission', 'reviewer', 'status', 'average_score', 'recommendation', 'assigned_at')
    list_filter = ('status', 'recommendation', 'is_anonymous', 'conflict_of_interest', 'assigned_at')
    search_fields = ('submission__title', 'reviewer__full_name', 'reviewer__username')
    ordering = ('-assigned_at',)
    
    # Поля для редактирования
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('submission', 'reviewer', 'status', 'recommendation')
        }),
        (_('Оценки'), {
            'fields': ('originality', 'scientific_value', 'methodology', 'presentation')
        }),
        (_('Комментарии'), {
            'fields': ('comments_for_author', 'comments_for_editor')
        }),
        (_('Настройки'), {
            'fields': ('is_anonymous', 'conflict_of_interest')
        }),
        (_('Даты'), {
            'fields': ('assigned_at', 'completed_at', 'created_at', 'updated_at')
        }),
    )
    
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
        return f"{obj.average_score:.1f}"
    average_score.short_description = "Средняя оценка"
    
    def get_queryset(self, request):
        """Оптимизированный запрос с select_related."""
        return super().get_queryset(request).select_related('submission', 'reviewer')
