from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import SiteSettings, Page, Contact, News, Redirect, EditorialTeam
from .models_extended import NewsLocale, PageLocale, Event, RawDocument, Affiliation

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Админка для настроек сайта."""
    
    def has_add_permission(self, request):
        """Запретить создание новых настроек."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Запретить удаление настроек."""
        return False

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    """Админка для страниц."""
    
    list_display = ('title', 'slug', 'is_published', 'is_in_menu', 'menu_order', 'created_at')
    list_filter = ('is_published', 'is_in_menu', 'created_at')
    search_fields = ('title', 'content')
    ordering = ('menu_order', 'title')
    
    # Поля для редактирования
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('title', 'slug', 'content')
        }),
        (_('SEO'), {
            'fields': ('meta_title', 'meta_description')
        }),
        (_('Настройки'), {
            'fields': ('is_published', 'is_in_menu', 'menu_order')
        }),
    )
    
    # Поля только для чтения
    readonly_fields = ('created_at', 'updated_at')
    
    # Действия
    actions = ['publish_pages', 'unpublish_pages', 'add_to_menu', 'remove_from_menu']
    
    def publish_pages(self, request, queryset):
        """Опубликовать выбранные страницы."""
        updated = queryset.update(is_published=True)
        self.message_user(request, f'{updated} страниц опубликовано.')
    publish_pages.short_description = "Опубликовать выбранные страницы"
    
    def unpublish_pages(self, request, queryset):
        """Снять с публикации выбранные страницы."""
        updated = queryset.update(is_published=False)
        self.message_user(request, f'{updated} страниц снято с публикации.')
    unpublish_pages.short_description = "Снять с публикации выбранные страницы"
    
    def add_to_menu(self, request, queryset):
        """Добавить в меню."""
        updated = queryset.update(is_in_menu=True)
        self.message_user(request, f'{updated} страниц добавлено в меню.')
    add_to_menu.short_description = "Добавить в меню"
    
    def remove_from_menu(self, request, queryset):
        """Убрать из меню."""
        updated = queryset.update(is_in_menu=False)
        self.message_user(request, f'{updated} страниц убрано из меню.')
    remove_from_menu.short_description = "Убрать из меню"

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """Админка для контактов."""
    
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    ordering = ('-created_at',)
    
    # Поля для редактирования
    fieldsets = (
        (_('Контактная информация'), {
            'fields': ('name', 'email', 'subject')
        }),
        (_('Сообщение'), {
            'fields': ('message',)
        }),
        (_('Статус'), {
            'fields': ('is_read',)
        }),
    )
    
    # Поля только для чтения
    readonly_fields = ('created_at',)
    
    # Действия
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        """Отметить как прочитанные."""
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} сообщений отмечено как прочитанные.')
    mark_as_read.short_description = "Отметить как прочитанные"
    
    def mark_as_unread(self, request, queryset):
        """Отметить как непрочитанные."""
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} сообщений отмечено как непрочитанные.')
    mark_as_unread.short_description = "Отметить как непрочитанные"

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    """Админка для новостей."""
    
    list_display = ('title', 'is_published', 'is_featured', 'published_at', 'created_at')
    list_filter = ('is_published', 'is_featured', 'published_at', 'created_at')
    search_fields = ('title', 'content', 'excerpt')
    ordering = ('-published_at', '-created_at')
    
    # Поля для редактирования
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('title', 'slug', 'content', 'excerpt')
        }),
        (_('Изображение'), {
            'fields': ('image',)
        }),
        (_('Настройки'), {
            'fields': ('is_published', 'is_featured', 'published_at')
        }),
    )
    
    # Поля только для чтения
    readonly_fields = ('created_at', 'updated_at')
    
    # Действия
    actions = ['publish_news', 'unpublish_news', 'feature_news', 'unfeature_news']
    
    def publish_news(self, request, queryset):
        """Опубликовать выбранные новости."""
        from django.utils import timezone
        updated = queryset.update(is_published=True, published_at=timezone.now())
        self.message_user(request, f'{updated} новостей опубликовано.')
    publish_news.short_description = "Опубликовать выбранные новости"
    
    def unpublish_news(self, request, queryset):
        """Снять с публикации выбранные новости."""
        updated = queryset.update(is_published=False)
        self.message_user(request, f'{updated} новостей снято с публикации.')
    unpublish_news.short_description = "Снять с публикации выбранные новости"
    
    def feature_news(self, request, queryset):
        """Сделать рекомендуемыми."""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} новостей сделано рекомендуемыми.')
    feature_news.short_description = "Сделать рекомендуемыми"
    
    def unfeature_news(self, request, queryset):
        """Убрать из рекомендуемых."""
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} новостей убрано из рекомендуемых.')
    unfeature_news.short_description = "Убрать из рекомендуемых"


@admin.register(Redirect)
class RedirectAdmin(admin.ModelAdmin):
    """Админка для редиректов."""
    list_display = ("old_url", "new_path", "http_status", "is_active", "updated_at")
    list_filter = ("is_active", "http_status")
    search_fields = ("old_url", "new_path")
    ordering = ("-updated_at",)
    readonly_fields = ("created_at", "updated_at")
    
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('old_url', 'new_path', 'http_status', 'is_active')
        }),
        (_('Даты'), {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(EditorialTeam)
class EditorialTeamAdmin(admin.ModelAdmin):
    """Админка для редакционной коллегии."""
    
    list_display = ('user', 'role', 'section', 'is_active', 'order', 'started_at')
    list_filter = ('role', 'is_active', 'section', 'started_at')
    search_fields = ('user__full_name', 'user__username', 'user__email', 'affiliation')
    ordering = ('order', 'role', 'user')
    
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('user', 'role', 'section', 'order', 'is_active')
        }),
        (_('Биография'), {
            'fields': ('bio_ru', 'bio_kk', 'bio_en')
        }),
        (_('Контактная информация'), {
            'fields': ('email', 'orcid', 'affiliation')
        }),
        (_('Даты работы'), {
            'fields': ('started_at', 'ended_at')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(NewsLocale)
class NewsLocaleAdmin(admin.ModelAdmin):
    """Админка для локализаций новостей."""
    list_display = ('news', 'language', 'title', 'updated_at')
    list_filter = ('language',)
    search_fields = ('news__title', 'title', 'body_html')
    ordering = ('news', 'language')


@admin.register(PageLocale)
class PageLocaleAdmin(admin.ModelAdmin):
    """Админка для локализаций страниц."""
    list_display = ('page', 'language', 'title', 'updated_at')
    list_filter = ('language',)
    search_fields = ('page__title', 'title', 'body_html')
    ordering = ('page', 'language')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Админка для событий."""
    list_display = ('object_type', 'object_id', 'kind', 'ip', 'timestamp')
    list_filter = ('object_type', 'kind', 'timestamp')
    search_fields = ('ip', 'user_agent')
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'


@admin.register(RawDocument)
class RawDocumentAdmin(admin.ModelAdmin):
    """Админка для сырых документов ETL."""
    list_display = ('source_url', 'sha256', 'fetched_at')
    list_filter = ('fetched_at',)
    search_fields = ('source_url', 'sha256')
    ordering = ('-fetched_at',)
    readonly_fields = ('sha256', 'fetched_at')
    date_hierarchy = 'fetched_at'


@admin.register(Affiliation)
class AffiliationAdmin(admin.ModelAdmin):
    """Админка для аффилиаций."""
    list_display = ('name', 'country', 'city', 'created_at')
    list_filter = ('country',)
    search_fields = ('name', 'name_en', 'country', 'city')
    ordering = ('name',)
