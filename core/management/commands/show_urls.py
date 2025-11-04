from django.core.management.base import BaseCommand
from django.urls import get_resolver


class Command(BaseCommand):
    help = 'Печатает все URL-паттерны: path | name | view | app'

    def handle(self, *args, **options):
        resolver = get_resolver()
        for pattern in resolver.url_patterns:
            self._print_pattern(pattern)

    def _print_pattern(self, pattern, prefix=''):
        try:
            regex = getattr(pattern.pattern, 'route', str(pattern.pattern))
        except Exception:
            regex = str(pattern.pattern)

        if hasattr(pattern, 'url_patterns'):
            # include
            for p in pattern.url_patterns:
                self._print_pattern(p, prefix + regex)
        else:
            name = pattern.name or ''
            callback = getattr(pattern.callback, '__name__', str(pattern.callback))
            module = getattr(pattern.callback, '__module__', '')
            self.stdout.write(f"/{prefix}{regex} | {name} | {module}.{callback}")


