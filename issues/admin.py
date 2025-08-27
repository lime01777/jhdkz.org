from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Issue

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    """Админка для модели выпуска."""
    
    list_display = ('year', 'number', 'title_ru', 'status', 'published_at', 'articles_count')
    list_filter = ('year', 'status', 'published_at')
    search_fields = ('title_ru', 'title_kk', 'title_en', 'description')
    ordering = ('-year', '-number')
    
    # Поля для редактирования
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('year', 'number', 'status', 'published_at')
        }),
        (_('Названия'), {
            'fields': ('title_ru', 'title_kk', 'title_en')
        }),
        (_('Файлы'), {
            'fields': ('cover_image', 'pdf_file')
        }),
        (_('Метаданные'), {
            'fields': ('description', 'keywords')
        }),
    )
    
    # Действия
    actions = ['publish_issues', 'archive_issues', 'make_draft']
    
    def publish_issues(self, request, queryset):
        """Опубликовать выбранные выпуски."""
        from django.utils import timezone
        updated = queryset.update(status='published', published_at=timezone.now())
        self.message_user(request, f'{updated} выпусков опубликовано.')
    publish_issues.short_description = "Опубликовать выбранные выпуски"
    
    def archive_issues(self, request, queryset):
        """Архивировать выбранные выпуски."""
        updated = queryset.update(status='archived')
        self.message_user(request, f'{updated} выпусков архивировано.')
    archive_issues.short_description = "Архивировать выбранные выпуски"
    
    def make_draft(self, request, queryset):
        """Сделать черновиками."""
        updated = queryset.update(status='draft')
        self.message_user(request, f'{updated} выпусков сделано черновиками.')
    make_draft.short_description = "Сделать черновиками"
    
    def articles_count(self, obj):
        """Количество статей в выпуске."""
        return obj.articles.count()
    articles_count.short_description = "Статей"
