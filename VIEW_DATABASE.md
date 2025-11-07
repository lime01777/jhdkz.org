# Как открыть и посмотреть базу данных локально

База данных SQLite находится в корне проекта: `db.sqlite3`

## Способ 1: Django Admin (самый простой)

### Шаг 1: Запустите сервер
```bash
python manage.py runserver
```

### Шаг 2: Откройте админку
Откройте в браузере: http://127.0.0.1:8000/admin/

### Шаг 3: Войдите под суперпользователем
Если у вас нет суперпользователя, создайте его:
```bash
python manage.py createsuperuser
```

В админке вы сможете просматривать и редактировать все модели:
- Пользователи (Users)
- Статьи (Articles)
- Выпуски (Issues)
- Новости (News)
- И другие модели

## Способ 2: DB Browser for SQLite (GUI приложение)

### Установка:
- **Windows**: Скачайте с https://sqlitebrowser.org/
- **Linux**: `sudo apt install sqlitebrowser`
- **Mac**: `brew install --cask db-browser-for-sqlite`

### Использование:
1. Откройте DB Browser for SQLite
2. Нажмите "Open Database"
3. Выберите файл `db.sqlite3` в корне проекта
4. Просматривайте таблицы, данные, выполняйте SQL запросы

## Способ 3: Командная строка sqlite3

### Windows (если установлен):
```bash
sqlite3 db.sqlite3
```

### Linux/Mac:
```bash
sqlite3 db.sqlite3
```

### Полезные команды SQLite:
```sql
-- Показать все таблицы
.tables

-- Показать структуру таблицы
.schema articles_article

-- Показать все данные из таблицы (первые 10 строк)
SELECT * FROM articles_article LIMIT 10;

-- Показать количество записей
SELECT COUNT(*) FROM articles_article;

-- Выполнить SQL запрос
SELECT title_ru, views, downloads FROM articles_article WHERE status='published';

-- Выход
.quit
```

## Способ 4: Django Shell (рекомендуется для программистов)

### Запуск Django shell:
```bash
python manage.py shell
```

### Примеры команд в shell:

```python
# Импорт моделей
from articles.models import Article
from issues.models import Issue
from users.models import User

# Получить все статьи
articles = Article.objects.all()
print(f"Всего статей: {articles.count()}")

# Получить опубликованные статьи
published = Article.objects.filter(status='published')
for article in published:
    print(f"{article.title_ru} - просмотров: {article.views}")

# Получить все выпуски
issues = Issue.objects.all()
for issue in issues:
    print(f"{issue.year} №{issue.number}: {issue.articles.count()} статей")

# Получить всех пользователей
users = User.objects.all()
print(f"Всего пользователей: {users.count()}")

# Получить авторов
authors = User.objects.filter(role='author')
print(f"Всего авторов: {authors.count()}")

# Получить конкретную статью
article = Article.objects.get(pk=1)
print(f"Статья: {article.title_ru}")
print(f"Авторы: {', '.join([author.username for author in article.authors.all()])}")

# Выполнить SQL запрос напрямую
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT COUNT(*) FROM articles_article WHERE status='published'")
count = cursor.fetchone()[0]
print(f"Опубликованных статей: {count}")

# Выход из shell
exit()
```

## Способ 5: Django Extensions (расширенный shell)

### Установка:
```bash
pip install django-extensions
```

Добавьте в `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    ...
    'django_extensions',
]
```

### Использование:
```bash
# Улучшенный shell с автозагрузкой моделей
python manage.py shell_plus

# Показать все модели и их связи
python manage.py graph_models -a -o models.png
```

## Способ 6: SQLite Studio (альтернативный GUI)

### Установка:
Скачайте с https://sqlitestudio.pl/

### Использование:
1. Откройте SQLite Studio
2. Database → Add Database
3. Выберите файл `db.sqlite3`
4. Просматривайте и редактируйте данные

## Способ 7: VS Code расширение

### Установка расширения:
1. Откройте VS Code
2. Установите расширение "SQLite Viewer" или "SQLite"
3. Откройте файл `db.sqlite3`
4. Просматривайте таблицы и данные прямо в редакторе

## Полезные SQL запросы для анализа данных

```sql
-- Количество статей по статусам
SELECT status, COUNT(*) as count 
FROM articles_article 
GROUP BY status;

-- Топ 10 статей по просмотрам
SELECT title_ru, views, downloads 
FROM articles_article 
WHERE status='published'
ORDER BY views DESC 
LIMIT 10;

-- Статистика по выпускам
SELECT i.year, i.number, COUNT(a.id) as articles_count
FROM issues_issue i
LEFT JOIN articles_article a ON a.issue_id = i.id
GROUP BY i.id
ORDER BY i.year DESC, i.number DESC;

-- Пользователи по ролям
SELECT role, COUNT(*) as count
FROM users_user
GROUP BY role;

-- Статьи с авторами
SELECT a.title_ru, u.username, u.full_name
FROM articles_article a
JOIN articles_article_authors aa ON aa.article_id = a.id
JOIN users_user u ON u.id = aa.user_id
WHERE a.status='published'
LIMIT 20;
```

## Экспорт данных

### Экспорт в CSV через Django shell:
```python
import csv
from articles.models import Article

with open('articles_export.csv', 'w', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['ID', 'Название', 'Просмотры', 'Загрузки', 'Статус'])
    
    for article in Article.objects.all():
        writer.writerow([
            article.id,
            article.title_ru,
            article.views,
            article.downloads,
            article.status
        ])
```

### Экспорт через SQLite:
```bash
sqlite3 db.sqlite3 <<EOF
.headers on
.mode csv
.output articles_export.csv
SELECT id, title_ru, views, downloads, status FROM articles_article;
.quit
EOF
```

## Резервное копирование

### Создать резервную копию:
```bash
# Windows
copy db.sqlite3 db.sqlite3.backup

# Linux/Mac
cp db.sqlite3 db.sqlite3.backup
```

### Или через SQLite:
```bash
sqlite3 db.sqlite3 ".backup db.sqlite3.backup"
```

## Восстановление из резервной копии:
```bash
# Windows
copy db.sqlite3.backup db.sqlite3

# Linux/Mac
cp db.sqlite3.backup db.sqlite3
```

---

**Рекомендация**: Для быстрого просмотра используйте Django Admin. Для глубокого анализа данных используйте Django Shell или DB Browser for SQLite.

