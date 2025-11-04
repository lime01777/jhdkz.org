from django.core.management.base import BaseCommand
from django.urls import reverse, NoReverseMatch


TARGETS = [
    ('issues:issue_detail', {'year': 2024, 'number': 1}),
    ('articles:article_detail', {'pk': 1}),
    ('core:author_detail', {'slug': 'demo'}),
    ('core:file_download', {'pk': 1}),
    ('core:news_list', {}),
    ('core:news_detail', {'slug': 'demo'}),
    ('core:search', {}),
    ('core:api_search', {}),
    ('core:healthz', {}),
]


class Command(BaseCommand):
    help = 'Проверка наличия ключевых маршрутов. Возвращает код 1 при несоответствиях.'

    def handle(self, *args, **options):
        missing = []
        for name, kwargs in TARGETS:
            try:
                reverse(name, kwargs=kwargs or None)
            except NoReverseMatch as e:
                missing.append((name, str(e)))
        if missing:
            for name, err in missing:
                self.stdout.write(self.style.ERROR(f'MISSING: {name} -> {err}'))
            exit(1)
        self.stdout.write(self.style.SUCCESS('Все целевые маршруты доступны для reverse().'))


