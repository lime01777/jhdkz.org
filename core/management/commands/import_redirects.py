import csv
from django.core.management.base import BaseCommand, CommandError
from core.models import Redirect


class Command(BaseCommand):
    help = "Импорт редиректов из CSV (old_url,new_path). Обновляет существующие."

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Путь к CSV файлу')

    def handle(self, *args, **options):
        path = options['csv_file']
        created = 0
        updated = 0
        try:
            with open(path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                required = {'old_url', 'new_path'}
                if not required.issubset(reader.fieldnames or []):
                    raise CommandError('CSV должен содержать заголовки old_url,new_path')
                for row in reader:
                    obj, is_created = Redirect.objects.update_or_create(
                        old_url=row['old_url'].strip(),
                        defaults={'new_path': row['new_path'].strip(), 'is_active': True}
                    )
                    if is_created:
                        created += 1
                    else:
                        updated += 1
        except FileNotFoundError:
            raise CommandError(f'Файл не найден: {path}')

        self.stdout.write(self.style.SUCCESS(f'Готово. Создано: {created}, обновлено: {updated}'))


