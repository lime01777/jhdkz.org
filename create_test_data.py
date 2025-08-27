#!/usr/bin/env python
"""
Скрипт для создания тестовых данных для портала Journal of Health Development
"""

import os
import sys
import django
from datetime import datetime, date
from django.utils import timezone

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jhdkz_portal.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import SiteSettings, News
from issues.models import Issue
from articles.models import Article
from users.models import User

User = get_user_model()

def create_test_data():
    """Создание тестовых данных"""
    
    print("Создание тестовых данных...")
    
    # Создание настроек сайта
    settings, created = SiteSettings.objects.get_or_create(
        pk=1,
        defaults={
            'site_name': 'Journal of Health Development',
            'site_description': 'Научный журнал по вопросам развития здравоохранения в Казахстане и Центральной Азии',
            'email': 'info@jhdkz.org',
            'phone': '+7 (717) 123-45-67',
            'address': 'Астана, Казахстан',
            'meta_description': 'Научный журнал по вопросам развития здравоохранения',
        }
    )
    if created:
        print("✓ Настройки сайта созданы")
    
    # Создание пользователей
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@jhdkz.org',
            'full_name': 'Администратор',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("✓ Администратор создан")
    
    # Создание авторов
    authors_data = [
        {
            'username': 'author1',
            'email': 'author1@example.com',
            'full_name': 'Иванов Иван Иванович',
            'organization': 'Национальный научный центр',
            'role': 'author',
        },
        {
            'username': 'author2',
            'email': 'author2@example.com',
            'full_name': 'Петров Петр Петрович',
            'organization': 'Медицинский университет',
            'role': 'author',
        },
        {
            'username': 'author3',
            'email': 'author3@example.com',
            'full_name': 'Сидоров Сидор Сидорович',
            'organization': 'Институт здравоохранения',
            'role': 'author',
        },
    ]
    
    authors = []
    for author_data in authors_data:
        author, created = User.objects.get_or_create(
            username=author_data['username'],
            defaults=author_data
        )
        if created:
            author.set_password('password123')
            author.save()
            print(f"✓ Автор {author.full_name} создан")
        authors.append(author)
    
    # Создание выпусков
    issues_data = [
        {
            'year': 2024,
            'number': 4,
            'title_ru': 'Развитие здравоохранения в Казахстане',
            'title_kk': 'Қазақстандағы денсаулық сақтау дамуы',
            'title_en': 'Health Development in Kazakhstan',
            'status': 'published',
            'published_at': date(2024, 12, 15),
        },
        {
            'year': 2024,
            'number': 3,
            'title_ru': 'Современные подходы к медицинскому образованию',
            'title_kk': 'Медициналық білім берудегі заманауи тәсілдер',
            'title_en': 'Modern Approaches to Medical Education',
            'status': 'published',
            'published_at': date(2024, 9, 15),
        },
        {
            'year': 2024,
            'number': 2,
            'title_ru': 'Эпидемиология и общественное здравоохранение',
            'title_kk': 'Эпидемиология және қоғамдық денсаулық сақтау',
            'title_en': 'Epidemiology and Public Health',
            'status': 'published',
            'published_at': date(2024, 6, 15),
        },
        {
            'year': 2024,
            'number': 1,
            'title_ru': 'Клинические исследования и практика',
            'title_kk': 'Клиникалық зерттеулер және тәжірибе',
            'title_en': 'Clinical Research and Practice',
            'status': 'published',
            'published_at': date(2024, 3, 15),
        },
    ]
    
    issues = []
    for issue_data in issues_data:
        issue, created = Issue.objects.get_or_create(
            year=issue_data['year'],
            number=issue_data['number'],
            defaults=issue_data
        )
        if created:
            print(f"✓ Выпуск {issue.year} №{issue.number} создан")
        issues.append(issue)
    
    # Создание статей
    articles_data = [
        {
            'title_ru': 'Анализ состояния здравоохранения в Казахстане',
            'title_kk': 'Қазақстандағы денсаулық сақтау күйін талдау',
            'title_en': 'Analysis of Healthcare Status in Kazakhstan',
            'abstract_ru': 'В статье представлен анализ современного состояния системы здравоохранения в Казахстане, рассмотрены основные проблемы и перспективы развития.',
            'abstract_kk': 'Мақалада Қазақстандағы денсаулық сақтау жүйесінің қазіргі күйі талданып, негізгі мәселелер мен даму перспективалары қарастырылған.',
            'abstract_en': 'The article presents an analysis of the current state of the healthcare system in Kazakhstan, considers the main problems and development prospects.',
            'keywords_ru': 'здравоохранение, Казахстан, анализ, развитие',
            'keywords_kk': 'денсаулық сақтау, Қазақстан, талдау, даму',
            'keywords_en': 'healthcare, Kazakhstan, analysis, development',
            'page_start': 1,
            'page_end': 15,
            'status': 'published',
            'language': 'ru',
            'views': 125,
            'downloads': 45,
        },
        {
            'title_ru': 'Современные методы медицинского образования',
            'title_kk': 'Медициналық білім берудегі заманауи әдістер',
            'title_en': 'Modern Methods of Medical Education',
            'abstract_ru': 'Рассмотрены современные подходы к организации медицинского образования, включая дистанционные технологии и симуляционное обучение.',
            'abstract_kk': 'Медициналық білім беруді ұйымдастырудағы заманауи тәсілдер, қашықтықтан оқыту технологиялары мен симуляциялық оқыту қарастырылған.',
            'abstract_en': 'Modern approaches to the organization of medical education are considered, including distance technologies and simulation training.',
            'keywords_ru': 'медицинское образование, дистанционное обучение, симуляция',
            'keywords_kk': 'медициналық білім беру, қашықтықтан оқыту, симуляция',
            'keywords_en': 'medical education, distance learning, simulation',
            'page_start': 16,
            'page_end': 30,
            'status': 'published',
            'language': 'ru',
            'views': 89,
            'downloads': 32,
        },
        {
            'title_ru': 'Эпидемиологический надзор за инфекционными заболеваниями',
            'title_kk': 'Жұқпалы ауруларға эпидемиологиялық қадағалау',
            'title_en': 'Epidemiological Surveillance of Infectious Diseases',
            'abstract_ru': 'Представлены результаты эпидемиологического надзора за инфекционными заболеваниями в Республике Казахстан.',
            'abstract_kk': 'Қазақстан Республикасында жұқпалы ауруларға эпидемиологиялық қадағалау нәтижелері көрсетілген.',
            'abstract_en': 'The results of epidemiological surveillance of infectious diseases in the Republic of Kazakhstan are presented.',
            'keywords_ru': 'эпидемиология, инфекционные заболевания, надзор',
            'keywords_kk': 'эпидемиология, жұқпалы аурулар, қадағалау',
            'keywords_en': 'epidemiology, infectious diseases, surveillance',
            'page_start': 31,
            'page_end': 45,
            'status': 'published',
            'language': 'ru',
            'views': 156,
            'downloads': 67,
        },
        {
            'title_ru': 'Клинические исследования новых методов лечения',
            'title_kk': 'Емдеудің жаңа әдістеріне клиникалық зерттеулер',
            'title_en': 'Clinical Studies of New Treatment Methods',
            'abstract_ru': 'Проведены клинические исследования эффективности новых методов лечения различных заболеваний.',
            'abstract_kk': 'Әртүрлі ауруларды емдеудің жаңа әдістерінің тиімділігіне клиникалық зерттеулер жүргізілген.',
            'abstract_en': 'Clinical studies of the effectiveness of new methods of treating various diseases have been conducted.',
            'keywords_ru': 'клинические исследования, лечение, эффективность',
            'keywords_kk': 'клиникалық зерттеулер, емдеу, тиімділік',
            'keywords_en': 'clinical studies, treatment, effectiveness',
            'page_start': 46,
            'page_end': 60,
            'status': 'published',
            'language': 'ru',
            'views': 203,
            'downloads': 89,
        },
    ]
    
    for i, article_data in enumerate(articles_data):
        article, created = Article.objects.get_or_create(
            title_ru=article_data['title_ru'],
            defaults={
                **article_data,
                'issue': issues[i % len(issues)],
            }
        )
        if created:
            # Добавляем авторов к статье
            article.authors.add(authors[i % len(authors)])
            if i > 0:
                article.authors.add(authors[(i + 1) % len(authors)])
            print(f"✓ Статья '{article.title_ru}' создана")
    
    # Создание новостей
    news_data = [
        {
            'title': 'Новый выпуск журнала опубликован',
            'slug': 'new-issue-published',
            'content': 'Опубликован новый выпуск журнала "Journal of Health Development" за 2024 год.',
            'excerpt': 'Новый выпуск содержит статьи по актуальным вопросам здравоохранения.',
            'is_published': True,
            'is_featured': True,
            'published_at': timezone.now(),
        },
        {
            'title': 'Конференция по медицинскому образованию',
            'slug': 'medical-education-conference',
            'content': 'Состоялась международная конференция по вопросам медицинского образования.',
            'excerpt': 'В конференции приняли участие ведущие специалисты в области медицинского образования.',
            'is_published': True,
            'is_featured': False,
            'published_at': timezone.now(),
        },
    ]
    
    for news_item in news_data:
        news, created = News.objects.get_or_create(
            slug=news_item['slug'],
            defaults=news_item
        )
        if created:
            print(f"✓ Новость '{news.title}' создана")
    
    print("\n✓ Тестовые данные успешно созданы!")
    print(f"✓ Создано: {len(authors)} авторов, {len(issues)} выпусков, {len(articles_data)} статей, {len(news_data)} новостей")

if __name__ == '__main__':
    create_test_data() 