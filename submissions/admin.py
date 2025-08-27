from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Submission

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    """Админка для модели отправки."""
    
    list_display = ('submission_id', 'title', 'corresponding_author', 'status', 'submitted_at', 'created_at')
    list_filter = ('status', 'language', 'submitted_at', 'created_at')
    search_fields = ('title', 'submission_id', 'corresponding_author__full_name', 'corresponding_author__username')
    ordering = ('-created_at',)
    
    # Фильтры в правой панели
    filter_horizontal = ('co_authors',)
    
    # Поля для редактирования
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('submission_id', 'title', 'abstract', 'keywords', 'language')
        }),
        (_('Авторы'), {
            'fields': ('corresponding_author', 'co_authors')
        }),
        (_('Файлы'), {
            'fields': ('manuscript_file', 'supplementary_files')
        }),
        (_('Статус и workflow'), {
            'fields': ('status', 'submitted_at')
        }),
        (_('Комментарии'), {
            'fields': ('author_comments', 'editor_comments')
        }),
    )
    
    # Поля только для чтения
    readonly_fields = ('submission_id', 'created_at', 'updated_at')
    
    # Действия
    actions = ['submit_manuscripts', 'send_to_review', 'accept_submissions', 'reject_submissions']
    
    def submit_manuscripts(self, request, queryset):
        """Отправить выбранные рукописи."""
        from django.utils import timezone
        updated = queryset.update(status='submitted', submitted_at=timezone.now())
        self.message_user(request, f'{updated} рукописей отправлено.')
    submit_manuscripts.short_description = "Отправить выбранные рукописи"
    
    def send_to_review(self, request, queryset):
        """Отправить на рецензирование."""
        updated = queryset.update(status='under_review')
        self.message_user(request, f'{updated} рукописей отправлено на рецензирование.')
    send_to_review.short_description = "Отправить на рецензирование"
    
    def accept_submissions(self, request, queryset):
        """Принять выбранные отправки."""
        updated = queryset.update(status='accepted')
        self.message_user(request, f'{updated} отправок принято.')
    accept_submissions.short_description = "Принять выбранные отправки"
    
    def reject_submissions(self, request, queryset):
        """Отклонить выбранные отправки."""
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} отправок отклонено.')
    reject_submissions.short_description = "Отклонить выбранные отправки"
    
    def get_queryset(self, request):
        """Оптимизированный запрос с select_related."""
        return super().get_queryset(request).select_related('corresponding_author')
