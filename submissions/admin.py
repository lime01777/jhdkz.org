from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Submission, Section, SubmissionFile, SubmissionAuthor

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    """Админка для модели отправки."""
    
    list_display = ('submission_id', 'title_ru', 'corresponding_author', 'status', 'submitted_at', 'created_at')
    list_filter = ('status', 'language', 'submitted_at', 'created_at', 'section')
    search_fields = ('title_ru', 'title_kk', 'title_en', 'submission_id', 'corresponding_author__full_name', 'corresponding_author__username')
    ordering = ('-created_at',)
    
    # Фильтры в правой панели
    filter_horizontal = ('co_authors',)
    
    # Поля для редактирования
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('submission_id', 'section', 'title_ru', 'title_kk', 'title_en', 
                      'abstract_ru', 'abstract_kk', 'abstract_en',
                      'keywords_ru', 'keywords_kk', 'keywords_en', 'language')
        }),
        (_('Авторы'), {
            'fields': ('corresponding_author', 'co_authors')
        }),
        (_('Файлы'), {
            'fields': ('manuscript_file',)
        }),
        (_('Статус и workflow'), {
            'fields': ('status', 'submission_type', 'assigned_editor', 'review_type',
                      'submitted_at', 'last_review_date', 'last_revision_date', 'editor_decision_date')
        }),
        (_('Исследовательская информация'), {
            'fields': ('research_field', 'methodology', 'funding')
        }),
        (_('Этические аспекты'), {
            'fields': ('ethics_approval', 'ethics_committee', 'conflict_of_interest', 'data_availability')
        }),
        (_('Комментарии'), {
            'fields': ('author_comments', 'editor_comments', 'editor_reviewer_comments')
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
        updated = queryset.update(status='reviewing')
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
        return super().get_queryset(request).select_related('corresponding_author', 'section', 'assigned_editor')
    
    def title_ru(self, obj):
        """Отображение названия."""
        return obj.title_ru[:50] + '...' if len(obj.title_ru) > 50 else obj.title_ru
    title_ru.short_description = "Название"


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    """Админка для разделов."""
    list_display = ('title_ru', 'slug', 'require_review', 'review_type', 'is_active', 'order')
    list_filter = ('is_active', 'require_review', 'review_type')
    search_fields = ('title_ru', 'title_kk', 'title_en', 'slug')
    prepopulated_fields = {'slug': ('title_ru',)}


@admin.register(SubmissionFile)
class SubmissionFileAdmin(admin.ModelAdmin):
    """Админка для файлов подачи."""
    list_display = ('submission', 'name', 'file_type', 'version', 'uploaded_at', 'uploaded_by')
    list_filter = ('file_type', 'version', 'uploaded_at')
    search_fields = ('submission__submission_id', 'name', 'description')
    ordering = ('-uploaded_at',)


@admin.register(SubmissionAuthor)
class SubmissionAuthorAdmin(admin.ModelAdmin):
    """Админка для авторов подачи."""
    list_display = ('submission', 'author', 'author_order', 'is_corresponding', 'is_principal')
    list_filter = ('is_corresponding', 'is_principal')
    search_fields = ('submission__submission_id', 'author__full_name', 'author__username')
