from django.db import models
from django.utils.translation import gettext_lazy as _

class SiteSettings(models.Model):
    """
    Настройки сайта.
    Синглтон для хранения основных настроек портала.
    """
    # Основная информация
    site_name = models.CharField("Название сайта", max_length=100, default="Journal of Health Development")
    site_description = models.TextField("Описание сайта", blank=True)
    
    # Контакты
    email = models.EmailField("Email", blank=True)
    phone = models.CharField("Телефон", max_length=20, blank=True)
    address = models.TextField("Адрес", blank=True)
    
    # Социальные сети
    facebook = models.URLField("Facebook", blank=True)
    twitter = models.URLField("Twitter", blank=True)
    linkedin = models.URLField("LinkedIn", blank=True)
    
    # Настройки
    is_maintenance_mode = models.BooleanField("Режим обслуживания", default=False)
    maintenance_message = models.TextField("Сообщение при обслуживании", blank=True)
    
    # SEO
    meta_keywords = models.CharField("Meta keywords", max_length=500, blank=True)
    meta_description = models.TextField("Meta description", blank=True)
    
    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

    def __str__(self):
        return "Настройки сайта"
    
    def save(self, *args, **kwargs):
        """Обеспечивает единственный экземпляр настроек."""
        self.pk = 1
        super().save(*args, **kwargs)

class Page(models.Model):
    """
    Статические страницы сайта.
    """
    title = models.CharField("Заголовок", max_length=200)
    slug = models.SlugField("URL", unique=True)
    content = models.TextField("Содержание")
    
    # SEO
    meta_title = models.CharField("Meta title", max_length=200, blank=True)
    meta_description = models.TextField("Meta description", blank=True)
    
    # Статус
    is_published = models.BooleanField("Опубликована", default=True)
    is_in_menu = models.BooleanField("Показывать в меню", default=False)
    menu_order = models.PositiveIntegerField("Порядок в меню", default=0)
    
    # Даты
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    
    class Meta:
        verbose_name = "Страница"
        verbose_name_plural = "Страницы"
        ordering = ['menu_order', 'title']

    def __str__(self):
        return self.title
    
    def get_meta_title(self):
        """Возвращает meta title или заголовок."""
        return self.meta_title or self.title

class Contact(models.Model):
    """
    Контактная информация.
    """
    name = models.CharField("Имя", max_length=100)
    email = models.EmailField("Email")
    subject = models.CharField("Тема", max_length=200)
    message = models.TextField("Сообщение")
    
    # Статус
    is_read = models.BooleanField("Прочитано", default=False)
    
    # Даты
    created_at = models.DateTimeField("Дата отправки", auto_now_add=True)
    
    class Meta:
        verbose_name = "Контакт"
        verbose_name_plural = "Контакты"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"

class News(models.Model):
    """
    Новости и анонсы.
    """
    title = models.CharField("Заголовок", max_length=200)
    slug = models.SlugField("URL", unique=True)
    content = models.TextField("Содержание")
    excerpt = models.TextField("Краткое описание", blank=True)
    
    # Изображение
    image = models.ImageField("Изображение", upload_to='news/', blank=True, null=True)
    
    # Статус
    is_published = models.BooleanField("Опубликована", default=True)
    is_featured = models.BooleanField("Рекомендуемая", default=False)
    
    # Даты
    published_at = models.DateTimeField("Дата публикации", null=True, blank=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    
    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Устанавливает дату публикации при первом сохранении."""
        from django.utils import timezone
        if not self.published_at and self.is_published:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
