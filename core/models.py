from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

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


class Redirect(models.Model):
    """Простая модель редиректов. Используется для миграции старых URL.
    TODO: при наличии django.contrib.redirects можно заменить на стандартную.
    """
    old_url = models.CharField("Старый URL", max_length=500, unique=True)
    new_path = models.CharField("Новый путь", max_length=500)
    is_active = models.BooleanField("Активен", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Редирект"
        verbose_name_plural = "Редиректы"
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.old_url} -> {self.new_path}"

    def get_absolute_url(self):
        return self.new_path


class EditorialTeam(models.Model):
    """
    Редакционная коллегия журнала (Editor-in-Chief, Section Editors и т.д.).
    """
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='editorial_roles',
        verbose_name="Пользователь"
    )
    
    # Роль в редакции
    ROLE_CHOICES = [
        ('editor_in_chief', 'Главный редактор'),
        ('deputy_editor', 'Заместитель главного редактора'),
        ('section_editor', 'Редактор раздела'),
        ('associate_editor', 'Ассоциированный редактор'),
        ('copy_editor', 'Редактор-корректор'),
        ('layout_editor', 'Редактор верстки'),
        ('production_editor', 'Редактор производства'),
    ]
    role = models.CharField("Роль", max_length=20, choices=ROLE_CHOICES)
    
    # Раздел (для редакторов разделов)
    section = models.ForeignKey(
        'submissions.Section',
        on_delete=models.SET_NULL,
        related_name='editors',
        null=True,
        blank=True,
        verbose_name="Раздел"
    )
    
    # Порядок отображения
    order = models.PositiveIntegerField("Порядок", default=0)
    
    # Биография
    bio_ru = models.TextField("Биография (русский)", blank=True)
    bio_kk = models.TextField("Биография (казахский)", blank=True)
    bio_en = models.TextField("Биография (английский)", blank=True)
    
    # Дополнительные поля
    email = models.EmailField("Email", blank=True)
    orcid = models.CharField("ORCID", max_length=19, blank=True)
    affiliation = models.CharField("Аффилиация", max_length=500, blank=True)
    
    # Статус
    is_active = models.BooleanField("Активен", default=True)
    
    # Даты
    started_at = models.DateField("Дата начала работы", null=True, blank=True)
    ended_at = models.DateField("Дата окончания работы", null=True, blank=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    
    class Meta:
        verbose_name = "Член редакционной коллегии"
        verbose_name_plural = "Редакционная коллегия"
        ordering = ['order', 'role', 'user']
        unique_together = ('user', 'role', 'section')
    
    def __str__(self):
        role_name = self.get_role_display()
        if self.section:
            return f"{self.user.get_full_name()} - {role_name} ({self.section.title_ru})"
        return f"{self.user.get_full_name()} - {role_name}"
    
    def get_bio(self, language='ru'):
        """Возвращает биографию на указанном языке."""
        bio_map = {
            'ru': self.bio_ru,
            'kk': self.bio_kk,
            'en': self.bio_en,
        }
        return bio_map.get(language, self.bio_ru) or self.bio_ru
    
    @property
    def is_editor_in_chief(self):
        """Проверяет, является ли главным редактором."""
        return self.role == 'editor_in_chief'
    
    @property
    def is_section_editor(self):
        """Проверяет, является ли редактором раздела."""
        return self.role == 'section_editor'
