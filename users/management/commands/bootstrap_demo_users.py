from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = (
        "Создаёт демо-пользователей: admin (superuser), editor (staff), author. "
        "Назначает базовые права редактору. Пароль по умолчанию: ChangeMe123!"
    )

    def add_arguments(self, parser):
        parser.add_argument('--password', type=str, default='ChangeMe123!', help='Пароль для всех демо-пользователей')

    def handle(self, *args, **options):
        password = options['password']
        User = get_user_model()

        # Создадим/обновим группу редакторов и базовые права
        editors_group, _ = Group.objects.get_or_create(name='Editors')
        perms = []
        # Права на основные модели контента
        models_to_grant = [
            ('articles', 'article'),
            ('issues', 'issue'),
            ('core', 'news'),
            ('core', 'page'),
        ]
        for app_label, model in models_to_grant:
            try:
                ct = ContentType.objects.get(app_label=app_label, model=model)
                perms += list(Permission.objects.filter(content_type=ct))
            except ContentType.DoesNotExist:
                continue
        editors_group.permissions.set(perms)

        users_data = [
            {
                'username': 'admin',
                'email': 'admin@example.com',
                'full_name': 'Portal Admin',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
            },
            {
                'username': 'editor',
                'email': 'editor@example.com',
                'full_name': 'Portal Editor',
                'role': 'editor',
                'is_staff': True,
                'is_superuser': False,
            },
            {
                'username': 'author',
                'email': 'author@example.com',
                'full_name': 'Portal Author',
                'role': 'author',
                'is_staff': False,
                'is_superuser': False,
            },
        ]

        created_or_updated = []
        for data in users_data:
            user, created = User.objects.get_or_create(username=data['username'], defaults={
                'email': data['email'],
                'full_name': data['full_name'],
                'role': data['role'],
                'is_staff': data['is_staff'],
                'is_superuser': data['is_superuser'],
            })
            # Обновляем поля на случай существования
            user.email = data['email']
            user.full_name = data['full_name']
            user.role = data['role']
            user.is_staff = data['is_staff']
            user.is_superuser = data['is_superuser']
            user.set_password(password)
            user.save()
            # Добавляем в группу редакторов при необходимости
            if data['username'] == 'editor':
                user.groups.add(editors_group)
            created_or_updated.append((user.username, created))

        # Выводим краткий отчёт с доступами
        self.stdout.write(self.style.SUCCESS('Демо-пользователи готовы:'))
        for username, created in created_or_updated:
            self.stdout.write(f" - {username} ({'создан' if created else 'обновлён'}) / пароль: {password}")
        self.stdout.write('Роли: admin=superuser, editor=staff+Editors, author=author')


