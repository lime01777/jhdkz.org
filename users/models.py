from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Расширенная модель пользователя для портала научного журнала.
    Включает роли, профиль и связи с ORCID.
    """
    # Основная информация
    full_name = models.CharField("ФИО", max_length=255, blank=True)
    organization = models.CharField("Организация", max_length=255, blank=True)
    orcid = models.CharField("ORCID", max_length=19, blank=True, help_text="Формат: 0000-0000-0000-0000")
    
    # Роли пользователя
    ROLE_CHOICES = [
        ('author', 'Автор'),
        ('reviewer', 'Рецензент'),
        ('editor', 'Редактор'),
        ('admin', 'Администратор'),
    ]
    role = models.CharField("Роль", max_length=10, choices=ROLE_CHOICES, default='author')
    
    # Профиль
    bio = models.TextField("Биография", blank=True)
    avatar = models.ImageField("Аватар", upload_to='avatars/', blank=True, null=True)
    
    # Дополнительные поля
    phone = models.CharField("Телефон", max_length=20, blank=True)
    address = models.TextField("Адрес", blank=True)
    
    # Настройки
    email_notifications = models.BooleanField("Email уведомления", default=True)
    
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ['username']

    def __str__(self):
        return self.full_name or self.username
    
    def get_full_name(self):
        """Возвращает полное имя пользователя."""
        return self.full_name or super().get_full_name()
    
    def is_author(self):
        """Проверяет, является ли пользователь автором."""
        return self.role == 'author'
    
    def is_reviewer(self):
        """Проверяет, является ли пользователь рецензентом."""
        return self.role == 'reviewer'
    
    def is_editor(self):
        """Проверяет, является ли пользователь редактором (включая администраторов)."""
        return self.role in ['editor', 'admin'] or self.is_staff
    
    def is_admin(self):
        """Проверяет, является ли пользователь администратором."""
        return self.role == 'admin'