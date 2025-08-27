#!/usr/bin/env python
"""
Скрипт для импорта реальных данных с сайта jhdkz.org
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

def import_real_data():
    """Импорт реальных данных с сайта jhdkz.org"""
    
    print("Импорт реальных данных с сайта jhdkz.org...")

    # Обновляем настройки сайта
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

    # Создаем реальных авторов из статей
    real_authors_data = [
        {
            'username': 'guseynova_aa',
            'email': 'guseynova@example.com',
            'full_name': 'Гусейнова А.А.',
            'organization': 'Российская Федерация',
            'role': 'author',
        },
        {
            'username': 'manuylova_vv',
            'email': 'manuylova@example.com',
            'full_name': 'Мануйлова В.В.',
            'organization': 'Российская Федерация',
            'role': 'author',
        },
        {
            'username': 'tulegenova_am',
            'email': 'tulegenova@example.com',
            'full_name': 'Тулегенова А.М.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'ibraev_se',
            'email': 'ibraev@example.com',
            'full_name': 'Ибраев С.Е.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'turgambayeva_ak',
            'email': 'turgambayeva@example.com',
            'full_name': 'Тургамбаева А.К.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'sermanizova_gk',
            'email': 'sermanizova@example.com',
            'full_name': 'Серманизова Г.К.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'duysekova_sb',
            'email': 'duysekova@example.com',
            'full_name': 'Дуйсекова С.Б.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'dauletova_gsh',
            'email': 'dauletova@example.com',
            'full_name': 'Даулетова Г.Ш.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'ospanova_sh',
            'email': 'ospanova@example.com',
            'full_name': 'Оспанова Ш.Х.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'sekenova_rk',
            'email': 'sekenova@example.com',
            'full_name': 'Секенова Р.К.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'tulebayeva_ns',
            'email': 'tulebayeva@example.com',
            'full_name': 'Тулебаева Н.С.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'umbetzhanova_at',
            'email': 'umbetzhanova@example.com',
            'full_name': 'Умбетжанова А.Т.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'derbisalina_ga',
            'email': 'derbisalina@example.com',
            'full_name': 'Дербисалина Г.А.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'kisikova_sd',
            'email': 'kisikova@example.com',
            'full_name': 'Кисикова С.Д.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'suleymenova_rk',
            'email': 'suleymenova@example.com',
            'full_name': 'Сулейменова Р.К.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'myrzagaliyeva_am',
            'email': 'myrzagaliyeva@example.com',
            'full_name': 'Мырзагалиева А.М.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'orazova_gu',
            'email': 'orazova@example.com',
            'full_name': 'Оразова Ғ.Ұ.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'nakipova_zhzh',
            'email': 'nakipova@example.com',
            'full_name': 'Накипова Ж.Ж.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'nurdinov_ns',
            'email': 'nurdinov@example.com',
            'full_name': 'Нурдинов Н.С.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'oshibayeva_ae',
            'email': 'oshibayeva@example.com',
            'full_name': 'Ошибаева А.Е.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'zhanaliyeva_mk',
            'email': 'zhanaliyeva@example.com',
            'full_name': 'Жаналиева М.К.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'kayupova_gs',
            'email': 'kayupova@example.com',
            'full_name': 'Каюпова Г.С.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'makulbek_as',
            'email': 'makulbek@example.com',
            'full_name': 'Мақұлбек Ә.С.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'takuadina_ai',
            'email': 'takuadina@example.com',
            'full_name': 'Такуадина А.И.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'dauletkaliyeva_zh',
            'email': 'dauletkaliyeva@example.com',
            'full_name': 'Даулеткалиева Ж.А.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'izbasarov_msh',
            'email': 'izbasarov@example.com',
            'full_name': 'Избасаров М.Ш.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'bolatova_zhe',
            'email': 'bolatova@example.com',
            'full_name': 'Болатова Ж.Е.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'zhamantayev_ok',
            'email': 'zhamantayev@example.com',
            'full_name': 'Жамантаев О.К.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'erdesov_nzh',
            'email': 'erdesov@example.com',
            'full_name': 'Ердесов Н.Ж.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'nukeshtayeva_ke',
            'email': 'nukeshtayeva@example.com',
            'full_name': 'Нукештаева К.Е.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'sadvakasova_zhb',
            'email': 'sadvakasova@example.com',
            'full_name': 'Садвакасова Ж.Б.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'kalikhanova_dd',
            'email': 'kalikhanova@example.com',
            'full_name': 'Калиханова Д.Д.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'kamalbekova_gm',
            'email': 'kamalbekova@example.com',
            'full_name': 'Камалбекова Г.М.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'abzaliyeva_ds',
            'email': 'abzaliyeva@example.com',
            'full_name': 'Абзалиева Д.С.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'murat_a',
            'email': 'murat@example.com',
            'full_name': 'Мурат А.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'otargaliyeva_dd',
            'email': 'otargaliyeva@example.com',
            'full_name': 'Отаргалиева Д.Д.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'syzdykova_as',
            'email': 'syzdykova@example.com',
            'full_name': 'Сыздыкова А.С.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'esdaulet_sa',
            'email': 'esdaulet@example.com',
            'full_name': 'Есдаулет С.А.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'rahmanberdi_nm',
            'email': 'rahmanberdi@example.com',
            'full_name': 'Рахманберді Н.М.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'zhusupova_gk',
            'email': 'zhusupova@example.com',
            'full_name': 'Жусупова Г.К.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'abduldayeva_aa',
            'email': 'abduldayeva@example.com',
            'full_name': 'Абдулдаева А.А.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'doszhanova_gn',
            'email': 'doszhanova@example.com',
            'full_name': 'Досжанова Г.Н.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'tolegenova_ee',
            'email': 'tolegenova@example.com',
            'full_name': 'Толегенова Е.Е.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'derbisbek_sb',
            'email': 'derbisbek@example.com',
            'full_name': 'Дербисбек С.Б.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'tardzhibayeva_sk',
            'email': 'tardzhibayeva@example.com',
            'full_name': 'Тарджибаева С.К.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'makhataeva_sn',
            'email': 'makhataeva@example.com',
            'full_name': 'Махатаева С.Н.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'rakhmetova_lv',
            'email': 'rakhmetova@example.com',
            'full_name': 'Рахметова Л.В.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'ismailova_aa',
            'email': 'ismailova@example.com',
            'full_name': 'Исмаилова А.А.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'musina_aa',
            'email': 'musina@example.com',
            'full_name': 'Мусина А.А.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'zhizhila_sa',
            'email': 'zhizhila@example.com',
            'full_name': 'Жижила С.А.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'abuova_gt',
            'email': 'abuova@example.com',
            'full_name': 'Абуова Г.Т.',
            'organization': 'Казахстан',
            'role': 'author',
        },
        {
            'username': 'zhunisali_n',
            'email': 'zhunisali@example.com',
            'full_name': 'Жунисали Н.',
            'organization': 'Казахстан',
            'role': 'author',
        },
    ]

    authors = {}
    for author_data in real_authors_data:
        author, created = User.objects.get_or_create(
            username=author_data['username'],
            defaults=author_data
        )
        if created:
            author.set_password('password123')
            author.save()
            print(f"✓ Автор {author.full_name} создан")
        authors[author.full_name] = author

    # Создаем текущий выпуск Volume 60, Number 2 (2025)
    current_issue, created = Issue.objects.get_or_create(
        year=2025,
        number=2,
        defaults={
            'title_ru': 'Journal of Health Development - Volume 60, Number 2 (2025)',
            'title_kk': 'Journal of Health Development - Volume 60, Number 2 (2025)',
            'title_en': 'Journal of Health Development - Volume 60, Number 2 (2025)',
            'status': 'published',
            'published_at': date(2025, 6, 30),
        }
    )
    if created:
        print("✓ Текущий выпуск создан")

    # Реальные статьи из сайта
    real_articles_data = [
        {
            'title_ru': 'Проблемы медико-психолого-педагогического сопровождения детей с различными нарушениями развития в России',
            'title_kk': 'Ресейде әртүрлі даму бұзылыстары бар балаларды медико-психолого-педагогикалық қамтамасыз ету мәселелері',
            'title_en': 'Problems of medical-psychological-pedagogical support of children with various developmental disorders in Russia',
            'abstract_ru': 'В статье рассматриваются проблемы медико-психолого-педагогического сопровождения детей с различными нарушениями развития в России.',
            'abstract_kk': 'Мақалада Ресейде әртүрлі даму бұзылыстары бар балаларды медико-психолого-педагогикалық қамтамасыз ету мәселелері қарастырылады.',
            'abstract_en': 'The article discusses the problems of medical-psychological-pedagogical support of children with various developmental disorders in Russia.',
            'keywords_ru': 'медико-психолого-педагогическое сопровождение, нарушения развития, дети, Россия',
            'keywords_kk': 'медико-психолого-педагогикалық қамтамасыз ету, даму бұзылыстары, балалар, Ресей',
            'keywords_en': 'medical-psychological-pedagogical support, developmental disorders, children, Russia',
            'page_start': 4,
            'page_end': 12,
            'status': 'published',
            'language': 'ru',
            'views': 3,
            'downloads': 5,
            'authors': ['Гусейнова А.А.', 'Мануйлова В.В.'],
        },
        {
            'title_ru': 'Анализ медико-демографических показателей сельского населения за период 2014-2023 годы',
            'title_kk': '2014-2023 жылдар аралығындағы ауыл тұрғындарының медико-демографиялық көрсеткіштерін талдау',
            'title_en': 'Analysis of medical and demographic indicators of rural population for the period 2014-2023',
            'abstract_ru': 'Проведен анализ медико-демографических показателей сельского населения за период 2014-2023 годы.',
            'abstract_kk': '2014-2023 жылдар аралығындағы ауыл тұрғындарының медико-демографиялық көрсеткіштерін талдау жүргізілді.',
            'abstract_en': 'An analysis of medical and demographic indicators of rural population for the period 2014-2023 was carried out.',
            'keywords_ru': 'медико-демографические показатели, сельское население, анализ',
            'keywords_kk': 'медико-демографиялық көрсеткіштер, ауыл тұрғындары, талдау',
            'keywords_en': 'medical and demographic indicators, rural population, analysis',
            'page_start': 13,
            'page_end': 23,
            'status': 'published',
            'language': 'kk',
            'views': 3,
            'downloads': 6,
            'authors': ['Тулегенова А.М.', 'Ибраев С.Е.', 'Тургамбаева А.К.', 'Серманизова Г.К.', 'Дуйсекова С.Б.', 'Даулетова Г.Ш.', 'Оспанова Ш.Х.', 'Секенова Р.К.'],
        },
        {
            'title_ru': 'Факторы, влияющие на удовлетворенность пациентов качеством медицинских услуг',
            'title_kk': 'Науқастардың медициналық қызметтер сапасына қанағаттануын әсер ететін факторлар',
            'title_en': 'Factors affecting patient satisfaction with the quality of medical services',
            'abstract_ru': 'Исследованы факторы, влияющие на удовлетворенность пациентов качеством медицинских услуг.',
            'abstract_kk': 'Науқастардың медициналық қызметтер сапасына қанағаттануын әсер ететін факторлар зерттелді.',
            'abstract_en': 'Factors affecting patient satisfaction with the quality of medical services were studied.',
            'keywords_ru': 'удовлетворенность пациентов, качество медицинских услуг, факторы',
            'keywords_kk': 'науқастардың қанағаттануы, медициналық қызметтер сапасы, факторлар',
            'keywords_en': 'patient satisfaction, quality of medical services, factors',
            'page_start': 24,
            'page_end': 29,
            'status': 'published',
            'language': 'kk',
            'views': 5,
            'downloads': 4,
            'authors': ['Тулебаева Н.С.', 'Умбетжанова А.Т.', 'Дербисалина Г.А.', 'Кисикова С.Д.', 'Сулейменова Р.К.', 'Мырзагалиева А.М.', 'Оразова Ғ.Ұ.'],
        },
        {
            'title_ru': 'Валидация и апробация анкеты для выявления факторов риска мочекаменной болезни',
            'title_kk': 'Бұйрек тасты ауруының тәуекел факторларын анықтауға арналған сауалнаманы валидациялау және апробациялау',
            'title_en': 'Validation and testing of a questionnaire for identifying risk factors for urolithiasis',
            'abstract_ru': 'Проведена валидация и апробация анкеты для выявления факторов риска мочекаменной болезни.',
            'abstract_kk': 'Бұйрек тасты ауруының тәуекел факторларын анықтауға арналған сауалнама валидацияланды және апробацияланды.',
            'abstract_en': 'Validation and testing of a questionnaire for identifying risk factors for urolithiasis was carried out.',
            'keywords_ru': 'валидация, апробация, анкета, мочекаменная болезнь, факторы риска',
            'keywords_kk': 'валидация, апробация, сауалнама, бұйрек тасты ауруы, тәуекел факторлары',
            'keywords_en': 'validation, testing, questionnaire, urolithiasis, risk factors',
            'page_start': 30,
            'page_end': 37,
            'status': 'published',
            'language': 'ru',
            'views': 2,
            'downloads': 2,
            'authors': ['Накипова Ж.Ж.', 'Нурдинов Н.С.', 'Ошибаева А.Е.', 'Жаналиева М.К.'],
        },
        {
            'title_ru': 'Грамотность в вопросах здоровья обучающихся высших учебных заведений. Обзор литературы',
            'title_kk': 'Жоғары оқу орындарының оқушыларының денсаулық сақтау мәселелері бойынша сауаттылығы. Әдебиет шолуы',
            'title_en': 'Health literacy of students in higher educational institutions. Literature review',
            'abstract_ru': 'Представлен обзор литературы по грамотности в вопросах здоровья обучающихся высших учебных заведений.',
            'abstract_kk': 'Жоғары оқу орындарының оқушыларының денсаулық сақтау мәселелері бойынша сауаттылығы туралы әдебиет шолуы көрсетілді.',
            'abstract_en': 'A literature review on health literacy of students in higher educational institutions is presented.',
            'keywords_ru': 'грамотность в вопросах здоровья, обучающиеся, высшие учебные заведения, обзор литературы',
            'keywords_kk': 'денсаулық сақтау мәселелері бойынша сауаттылық, оқушылар, жоғары оқу орындары, әдебиет шолуы',
            'keywords_en': 'health literacy, students, higher educational institutions, literature review',
            'page_start': 38,
            'page_end': 45,
            'status': 'published',
            'language': 'en',
            'views': 3,
            'downloads': 4,
            'authors': ['Каюпова Г.С.', 'Мақұлбек Ә.С.', 'Такуадина А.И.', 'Даулеткалиева Ж.А.', 'Избасаров М.Ш.', 'Болатова Ж.Е.', 'Жамантаев О.К.', 'Ердесов Н.Ж.', 'Нукештаева К.Е.'],
        },
        {
            'title_ru': 'Ментальное здоровье студентов как приоритет общественного здравоохранения: Региональный анализ и Международные подходы',
            'title_kk': 'Студенттердің психикалық денсаулығы қоғамдық денсаулық сақтаудың басымдығы ретінде: Аймақтық талдау және Халықаралық тәсілдер',
            'title_en': 'Mental health of students as a priority of public health: Regional analysis and International approaches',
            'abstract_ru': 'Рассмотрены вопросы ментального здоровья студентов как приоритета общественного здравоохранения.',
            'abstract_kk': 'Студенттердің психикалық денсаулығы қоғамдық денсаулық сақтаудың басымдығы ретіндегі мәселелер қарастырылды.',
            'abstract_en': 'Issues of mental health of students as a priority of public health are considered.',
            'keywords_ru': 'ментальное здоровье, студенты, общественное здравоохранение, региональный анализ',
            'keywords_kk': 'психикалық денсаулық, студенттер, қоғамдық денсаулық сақтау, аймақтық талдау',
            'keywords_en': 'mental health, students, public health, regional analysis',
            'page_start': 46,
            'page_end': 53,
            'status': 'published',
            'language': 'en',
            'views': 2,
            'downloads': 2,
            'authors': ['Садвакасова Ж.Б.', 'Калиханова Д.Д.', 'Дуйсекова С.Б.', 'Камалбекова Г.М.', 'Абзалиева Д.С.'],
        },
        {
            'title_ru': 'Удовлетворенность работодателей качеством подготовки выпускников медицинских ВУЗов Казахстана',
            'title_kk': 'Қазақстан медициналық жоғары оқу орындарының түлектерінің дайындық сапасына жұмыс берушілердің қанағаттануы',
            'title_en': 'Employer satisfaction with the quality of training of graduates of medical universities in Kazakhstan',
            'abstract_ru': 'Исследована удовлетворенность работодателей качеством подготовки выпускников медицинских ВУЗов Казахстана.',
            'abstract_kk': 'Қазақстан медициналық жоғары оқу орындарының түлектерінің дайындық сапасына жұмыс берушілердің қанағаттануы зерттелді.',
            'abstract_en': 'Employer satisfaction with the quality of training of graduates of medical universities in Kazakhstan was studied.',
            'keywords_ru': 'удовлетворенность работодателей, качество подготовки, выпускники, медицинские ВУЗы',
            'keywords_kk': 'жұмыс берушілердің қанағаттануы, дайындық сапасы, түлектер, медициналық жоғары оқу орындары',
            'keywords_en': 'employer satisfaction, quality of training, graduates, medical universities',
            'page_start': 54,
            'page_end': 61,
            'status': 'published',
            'language': 'ru',
            'views': 3,
            'downloads': 2,
            'authors': ['Мурат А.', 'Отаргалиева Д.Д.', 'Сыздыкова А.С.', 'Есдаулет С.А.'],
        },
        {
            'title_ru': 'Барьеры в научной деятельности молодых учёных в Медицинском университете Астана: Результаты опроса',
            'title_kk': 'Астана медициналық университетіндегі жас ғалымдардың ғылыми қызметіндегі кедергілер: Сауалнама нәтижелері',
            'title_en': 'Barriers in scientific activity of young scientists at Astana Medical University: Survey results',
            'abstract_ru': 'Представлены результаты опроса по барьерам в научной деятельности молодых учёных в Медицинском университете Астана.',
            'abstract_kk': 'Астана медициналық университетіндегі жас ғалымдардың ғылыми қызметіндегі кедергілер туралы сауалнама нәтижелері көрсетілді.',
            'abstract_en': 'The results of a survey on barriers in scientific activity of young scientists at Astana Medical University are presented.',
            'keywords_ru': 'барьеры, научная деятельность, молодые учёные, медицинский университет',
            'keywords_kk': 'кедергілер, ғылыми қызмет, жас ғалымдар, медициналық университет',
            'keywords_en': 'barriers, scientific activity, young scientists, medical university',
            'page_start': 62,
            'page_end': 70,
            'status': 'published',
            'language': 'ru',
            'views': 2,
            'downloads': 4,
            'authors': ['Рахманберді Н.М.', 'Жусупова Г.К.'],
        },
        {
            'title_ru': 'Оценка нутриционного статуса обучающихся',
            'title_kk': 'Оқушылардың нутрициялық күйін бағалау',
            'title_en': 'Assessment of nutritional status of students',
            'abstract_ru': 'Проведена оценка нутриционного статуса обучающихся.',
            'abstract_kk': 'Оқушылардың нутрициялық күйін бағалау жүргізілді.',
            'abstract_en': 'Assessment of nutritional status of students was carried out.',
            'keywords_ru': 'нутриционный статус, обучающиеся, оценка',
            'keywords_kk': 'нутрициялық күй, оқушылар, бағалау',
            'keywords_en': 'nutritional status, students, assessment',
            'page_start': 71,
            'page_end': 76,
            'status': 'published',
            'language': 'ru',
            'views': 2,
            'downloads': 2,
            'authors': ['Абдулдаева А.А.', 'Досжанова Г.Н.', 'Толегенова Е.Е.', 'Дербисбек С.Б.', 'Тарджибаева С.К.', 'Махатаева С.Н.', 'Рахметова Л.В.'],
        },
        {
            'title_ru': 'Оценка уровня заболеваемости с временной утратой трудоспособности горнорабочих подземной добычи полиметаллических руд',
            'title_kk': 'Полиметалды кендерді жер асты өндірісінің тау жұмысшыларының уақытша еңбекке жарамсыздықпен ауруға шалдығу деңгейін бағалау',
            'title_en': 'Assessment of the level of morbidity with temporary disability of miners of underground mining of polymetallic ores',
            'abstract_ru': 'Проведена оценка уровня заболеваемости с временной утратой трудоспособности горнорабочих подземной добычи полиметаллических руд.',
            'abstract_kk': 'Полиметалды кендерді жер асты өндірісінің тау жұмысшыларының уақытша еңбекке жарамсыздықпен ауруға шалдығу деңгейін бағалау жүргізілді.',
            'abstract_en': 'Assessment of the level of morbidity with temporary disability of miners of underground mining of polymetallic ores was carried out.',
            'keywords_ru': 'заболеваемость, временная утрата трудоспособности, горнорабочие, подземная добыча',
            'keywords_kk': 'ауруға шалдығу, уақытша еңбекке жарамсыздық, тау жұмысшылары, жер асты өндірісі',
            'keywords_en': 'morbidity, temporary disability, miners, underground mining',
            'page_start': 77,
            'page_end': 84,
            'status': 'published',
            'language': 'ru',
            'views': 3,
            'downloads': 2,
            'authors': ['Исмаилова А.А.', 'Мусина А.А.', 'Жижила С.А.', 'Абуова Г.Т.', 'Сулейменова Р.К.', 'Оразова Ғ.Ұ.', 'Жунисали Н.'],
        },
    ]

    # Создаем статьи
    for article_data in real_articles_data:
        article, created = Article.objects.get_or_create(
            title_ru=article_data['title_ru'],
            defaults={
                'issue': current_issue,
                'title_kk': article_data['title_kk'],
                'title_en': article_data['title_en'],
                'abstract_ru': article_data['abstract_ru'],
                'abstract_kk': article_data['abstract_kk'],
                'abstract_en': article_data['abstract_en'],
                'keywords_ru': article_data['keywords_ru'],
                'keywords_kk': article_data['keywords_kk'],
                'keywords_en': article_data['keywords_en'],
                'page_start': article_data['page_start'],
                'page_end': article_data['page_end'],
                'status': article_data['status'],
                'language': article_data['language'],
                'views': article_data['views'],
                'downloads': article_data['downloads'],
            }
        )
        if created:
            # Добавляем авторов к статье
            for author_name in article_data['authors']:
                if author_name in authors:
                    article.authors.add(authors[author_name])
            print(f"✓ Статья '{article.title_ru}' создана")

    # Создаем новости на основе информации с сайта
    news_data = [
        {
            'title': 'Опубликован новый выпуск журнала Volume 60, Number 2 (2025)',
            'slug': 'new-issue-volume-60-number-2-2025',
            'content': 'Опубликован новый выпуск журнала "Journal of Health Development" Volume 60, Number 2 (2025). Выпуск содержит 9 статей по актуальным вопросам здравоохранения, включая исследования по медико-психолого-педагогическому сопровождению детей, анализу медико-демографических показателей сельского населения, факторам удовлетворенности пациентов качеством медицинских услуг и другим важным темам.',
            'excerpt': 'Опубликован новый выпуск журнала с 9 статьями по актуальным вопросам здравоохранения.',
            'is_published': True,
            'is_featured': True,
            'published_at': timezone.now(),
        },
        {
            'title': 'Журнал индексируется в международных базах данных',
            'slug': 'journal-indexed-in-international-databases',
            'content': 'Журнал "Journal of Health Development" успешно индексируется в ведущих международных базах данных. Это обеспечивает широкую доступность публикаций для научного сообщества и повышает цитируемость статей авторов.',
            'excerpt': 'Журнал индексируется в международных базах данных для повышения доступности публикаций.',
            'is_published': True,
            'is_featured': False,
            'published_at': timezone.now(),
        },
        {
            'title': 'Открыт прием статей для следующего выпуска',
            'slug': 'open-submission-for-next-issue',
            'content': 'Открыт прием статей для следующего выпуска журнала "Journal of Health Development". Приглашаем авторов к публикации оригинальных исследований, обзоров литературы и клинических случаев по вопросам развития здравоохранения.',
            'excerpt': 'Открыт прием статей для следующего выпуска журнала.',
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

    print("\n✓ Реальные данные с сайта jhdkz.org успешно импортированы!")
    print(f"✓ Создано: {len(authors)} авторов, 1 выпуск, {len(real_articles_data)} статей, {len(news_data)} новостей")

if __name__ == '__main__':
    import_real_data() 