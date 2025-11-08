from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('submissions', '0004_add_test_section'),
        ('articles', '0004_populate_article_slugs'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='submission',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name='articles',
                to='submissions.submission',
                verbose_name='Подача',
            ),
        ),
    ]

