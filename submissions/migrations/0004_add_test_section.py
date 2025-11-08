from django.db import migrations


def create_test_section(apps, schema_editor):
    Section = apps.get_model('submissions', 'Section')
    if not Section.objects.filter(slug='test-section').exists():
        Section.objects.create(
            title_ru='Тестовый раздел',
            title_kk='Сынақ бөлімі',
            title_en='Test Section',
            slug='test-section',
            description='Раздел для тестовых публикаций и проверки функционала.',
            is_active=True,
            order=0,
            require_review=True,
            review_type='double',
        )


def delete_test_section(apps, schema_editor):
    Section = apps.get_model('submissions', 'Section')
    Section.objects.filter(slug='test-section').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('submissions', '0003_section_remove_submission_abstract_and_more'),
    ]

    operations = [
        migrations.RunPython(create_test_section, delete_test_section),
    ]

