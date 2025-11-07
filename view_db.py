#!/usr/bin/env python
"""
Скрипт для быстрого просмотра базы данных.
Использование: python view_db.py
"""
import os
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jhdkz_portal.settings.dev')
django.setup()

from articles.models import Article
from issues.models import Issue
from users.models import User
from core.models import News
from django.db.models import Count, Sum

def print_separator(title):
    """Печатает разделитель с заголовком."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def view_statistics():
    """Показывает общую статистику."""
    print_separator("ОБЩАЯ СТАТИСТИКА")
    
    # Статьи
    total_articles = Article.objects.count()
    published_articles = Article.objects.filter(status='published').count()
    print(f"\n📄 Статьи:")
    print(f"   Всего: {total_articles}")
    print(f"   Опубликовано: {published_articles}")
    
    total_views = Article.objects.aggregate(total=Sum('views'))['total'] or 0
    total_downloads = Article.objects.aggregate(total=Sum('downloads'))['total'] or 0
    print(f"   Просмотров: {total_views}")
    print(f"   Загрузок: {total_downloads}")
    
    # Выпуски
    total_issues = Issue.objects.count()
    published_issues = Issue.objects.filter(status='published').count()
    print(f"\n📚 Выпуски:")
    print(f"   Всего: {total_issues}")
    print(f"   Опубликовано: {published_issues}")
    
    # Пользователи
    total_users = User.objects.count()
    authors = User.objects.filter(role='author').count()
    editors = User.objects.filter(role='editor').count()
    reviewers = User.objects.filter(role='reviewer').count()
    print(f"\n👥 Пользователи:")
    print(f"   Всего: {total_users}")
    print(f"   Авторов: {authors}")
    print(f"   Редакторов: {editors}")
    print(f"   Рецензентов: {reviewers}")
    
    # Новости
    total_news = News.objects.count()
    print(f"\n📰 Новости:")
    print(f"   Всего: {total_news}")

def view_articles():
    """Показывает список статей."""
    print_separator("СТАТЬИ")
    
    articles = Article.objects.filter(status='published').order_by('-views')[:10]
    
    if not articles:
        print("   Нет опубликованных статей")
        return
    
    print(f"\nТоп-10 статей по просмотрам:\n")
    for i, article in enumerate(articles, 1):
        authors_str = ", ".join([author.username for author in article.authors.all()[:3]])
        if article.authors.count() > 3:
            authors_str += "..."
        print(f"{i}. {article.title_ru[:50]}")
        print(f"   Авторы: {authors_str}")
        print(f"   Просмотры: {article.views}, Загрузки: {article.downloads}")
        print(f"   Выпуск: {article.issue.year} №{article.issue.number}")
        print()

def view_issues():
    """Показывает список выпусков."""
    print_separator("ВЫПУСКИ")
    
    issues = Issue.objects.filter(status='published').order_by('-year', '-number')
    
    if not issues:
        print("   Нет опубликованных выпусков")
        return
    
    print("\nОпубликованные выпуски:\n")
    for issue in issues:
        articles_count = issue.articles.filter(status='published').count()
        print(f"📅 {issue.year} №{issue.number}: {issue.title_ru}")
        print(f"   Статей: {articles_count}")
        if issue.published_at:
            print(f"   Опубликован: {issue.published_at}")
        print()

def view_users():
    """Показывает список пользователей."""
    print_separator("ПОЛЬЗОВАТЕЛИ")
    
    authors = User.objects.filter(role='author').order_by('-date_joined')[:10]
    
    if not authors:
        print("   Нет зарегистрированных авторов")
        return
    
    print("\nПоследние 10 зарегистрированных авторов:\n")
    for author in authors:
        articles_count = author.articles.filter(status='published').count()
        print(f"👤 {author.username} ({author.full_name or 'Без имени'})")
        print(f"   Email: {author.email}")
        print(f"   Статей: {articles_count}")
        print(f"   Зарегистрирован: {author.date_joined.strftime('%Y-%m-%d')}")
        print()

def view_articles_by_status():
    """Показывает статистику по статусам статей."""
    print_separator("СТАТЬИ ПО СТАТУСАМ")
    
    from django.db.models import Count
    
    statuses = Article.objects.values('status').annotate(count=Count('id')).order_by('-count')
    
    status_names = {
        'draft': 'Черновик',
        'submitted': 'Отправлена',
        'review': 'На рецензии',
        'accepted': 'Принята',
        'rejected': 'Отклонена',
        'published': 'Опубликована',
    }
    
    print("\nРаспределение статей по статусам:\n")
    for status_info in statuses:
        status = status_info['status']
        count = status_info['count']
        name = status_names.get(status, status)
        print(f"   {name}: {count}")

def main():
    """Главная функция."""
    print("\n" + "=" * 60)
    print("  ПРОСМОТР БАЗЫ ДАННЫХ - Journal of Health Development")
    print("=" * 60)
    
    try:
        view_statistics()
        view_articles_by_status()
        view_articles()
        view_issues()
        view_users()
        
        print_separator("КОНЕЦ")
        print("\n💡 Для детального просмотра используйте Django Admin:")
        print("   python manage.py runserver")
        print("   http://127.0.0.1:8000/admin/")
        print("\n💡 Или Django Shell:")
        print("   python manage.py shell")
        print()
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

