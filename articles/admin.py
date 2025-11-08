from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Article
from .models_extended import ArticleLocale, Keyword, ArticleFile

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Админка для модели статьи."""
    
    list_display = ('title_ru', 'issue', 'status', 'authors_list', 'views', 'downloads', 'created_at')
    list_filter = ('status', 'issue', 'language', 'created_at', 'published_at')
    search_fields = ('title_ru', 'title_kk', 'title_en', 'abstract_ru', 'keywords_ru')
    ordering = ('-created_at',)
    
    # Фильтры в правой панели
    filter_horizontal = ('authors',)
    
    # Поля для редактирования
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('issue', 'submission', 'status', 'language', 'doi')
        }),
        (_('Названия'), {
            'fields': ('title_ru', 'title_kk', 'title_en')
        }),
        (_('Аннотации'), {
            'fields': ('abstract_ru', 'abstract_kk', 'abstract_en')
        }),
        (_('Ключевые слова'), {
            'fields': ('keywords_ru', 'keywords_kk', 'keywords_en')
        }),
        (_('Авторы'), {
            'fields': ('authors',)
        }),
        (_('Техническая информация'), {
            'fields': ('page_start', 'page_end', 'pdf_file')
        }),
        (_('Даты'), {
            'fields': ('submitted_at', 'published_at')
        }),
    )
    
    # Поля только для чтения
    readonly_fields = ('submission', 'views', 'downloads', 'created_at', 'updated_at')
    
    # Действия
    actions = ['publish_articles', 'accept_articles', 'reject_articles', 'reset_views']
    
    def publish_articles(self, request, queryset):
        """Опубликовать выбранные статьи."""
        from django.utils import timezone
        updated = queryset.update(status='published', published_at=timezone.now())
        self.message_user(request, f'{updated} статей опубликовано.')
    publish_articles.short_description = "Опубликовать выбранные статьи"
    
    def accept_articles(self, request, queryset):
        """Принять выбранные статьи."""
        updated = queryset.update(status='accepted')
        self.message_user(request, f'{updated} статей принято.')
    accept_articles.short_description = "Принять выбранные статьи"
    
    def reject_articles(self, request, queryset):
        """Отклонить выбранные статьи."""
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} статей отклонено.')
    reject_articles.short_description = "Отклонить выбранные статьи"
    
    def reset_views(self, request, queryset):
        """Сбросить счетчики просмотров."""
        updated = queryset.update(views=0, downloads=0)
        self.message_user(request, f'Счетчики сброшены для {updated} статей.')
    reset_views.short_description = "Сбросить счетчики просмотров"
    
    def authors_list(self, obj):
        """Список авторов."""
        authors = obj.authors.all()
        if authors:
            return ', '.join([author.get_full_name() for author in authors])
        return '-'
    authors_list.short_description = "Авторы"
    
    def get_queryset(self, request):
        """Оптимизированный запрос с prefetch_related."""
        return super().get_queryset(request).prefetch_related('authors', 'issue')


@admin.register(ArticleLocale)
class ArticleLocaleAdmin(admin.ModelAdmin):
    """Админка для локализаций статей."""
    list_display = ('article', 'language', 'title', 'updated_at')
    list_filter = ('language',)
    search_fields = ('article__title_ru', 'title', 'abstract', 'body_html')
    ordering = ('article', 'language')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    """Админка для ключевых слов."""
    list_display = ('term', 'language', 'articles_count', 'created_at')
    list_filter = ('language',)
    search_fields = ('term',)
    ordering = ('term', 'language')
    filter_horizontal = ('articles',)
    
    def articles_count(self, obj):
        """Количество статей с этим ключевым словом."""
        return obj.articles.count()
    articles_count.short_description = "Количество статей"


@admin.register(ArticleFile)
class ArticleFileAdmin(admin.ModelAdmin):
    """Админка для файлов статей."""
    list_display = ('article', 'kind', 'original_name', 'size', 'created_at')
    list_filter = ('kind', 'created_at')
    search_fields = ('article__title_ru', 'original_name', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('size', 'created_at', 'updated_at')
    
    def get_queryset(self, request):
        """Оптимизированный запрос."""
        return super().get_queryset(request).select_related('article')
