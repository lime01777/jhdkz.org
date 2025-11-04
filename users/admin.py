from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админка для модели пользователя."""
    
    list_display = ('username', 'full_name', 'email', 'role', 'organization', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'full_name', 'email', 'organization')
    ordering = ('-date_joined',)
    
    # Поля для редактирования
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Персональная информация'), {
            'fields': ('full_name', 'email', 'organization', 'orcid', 'phone', 'address')
        }),
        (_('Роль и права'), {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Профиль'), {
            'fields': ('bio', 'avatar', 'email_notifications')
        }),
        (_('Важные даты'), {'fields': ('last_login', 'date_joined')}),
    )
    
    # Поля для создания нового пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'full_name', 'email', 'password1', 'password2', 'role'),
        }),
    )
    
    # Действия
    actions = ['activate_users', 'deactivate_users', 'make_editors', 'make_reviewers']
    
    def activate_users(self, request, queryset):
        """Активировать выбранных пользователей."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} пользователей активировано.')
    activate_users.short_description = "Активировать выбранных пользователей"
    
    def deactivate_users(self, request, queryset):
        """Деактивировать выбранных пользователей."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} пользователей деактивировано.')
    deactivate_users.short_description = "Деактивировать выбранных пользователей"
    
    def make_editors(self, request, queryset):
        """Назначить редакторами."""
        updated = queryset.update(role='editor')
        self.message_user(request, f'{updated} пользователей назначено редакторами.')
    make_editors.short_description = "Назначить редакторами"
    
    def make_reviewers(self, request, queryset):
        """Назначить рецензентами."""
        updated = queryset.update(role='reviewer')
        self.message_user(request, f'{updated} пользователей назначено рецензентами.')
    make_reviewers.short_description = "Назначить рецензентами"
