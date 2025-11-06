"""
Миграция данных: заполняет slug для существующих выпусков.
"""
from django.db import migrations
from django.utils.text import slugify


def populate_issue_slugs(apps, schema_editor):
    """Заполняет slug для существующих выпусков на основе year и number."""
    Issue = apps.get_model('issues', 'Issue')
    
    for issue in Issue.objects.filter(slug__isnull=True):
        slug = slugify(f"{issue.year}-{issue.number}")
        
        # Проверяем уникальность
        counter = 1
        original_slug = slug
        while Issue.objects.filter(slug=slug).exclude(pk=issue.pk).exists():
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        issue.slug = slug
        issue.save(update_fields=['slug'])


def reverse_populate_issue_slugs(apps, schema_editor):
    """Обратная операция - не требуется, slug остается."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0002_issue_slug_issue_issues_issu_year_6149c4_idx_and_more'),
    ]

    operations = [
        migrations.RunPython(populate_issue_slugs, reverse_populate_issue_slugs),
    ]

