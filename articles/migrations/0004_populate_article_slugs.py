"""
Миграция данных: заполняет slug для существующих статей.
"""
from django.db import migrations
from django.utils.text import slugify


def populate_article_slugs(apps, schema_editor):
    """Заполняет slug для существующих статей на основе title_ru."""
    Article = apps.get_model('articles', 'Article')
    
    for article in Article.objects.filter(slug__isnull=True):
        # Используем title_ru или pk как fallback
        if article.title_ru and article.title_ru.strip():
            base_slug = slugify(article.title_ru)[:500]
        else:
            # Если заголовок пустой, используем pk
            base_slug = f"article-{article.pk}"
        
        # Если slugify вернул пустую строку, используем pk
        if not base_slug:
            base_slug = f"article-{article.pk}"
        
        slug = base_slug
        counter = 1
        
        # Проверяем уникальность
        while Article.objects.filter(slug=slug).exclude(pk=article.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        article.slug = slug
        article.save(update_fields=['slug'])


def reverse_populate_article_slugs(apps, schema_editor):
    """Обратная операция - не требуется, slug остается."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0003_articlefile_articlelocale_keyword_article_section_and_more'),
    ]

    operations = [
        migrations.RunPython(populate_article_slugs, reverse_populate_article_slugs),
    ]

