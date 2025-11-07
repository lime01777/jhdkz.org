"""
Базовые настройки Django проекта jhdkz_portal.
Общие настройки для dev и prod окружений.
"""
import os
from pathlib import Path
import environ

# PROJECT_DIR = каталог 'jhdkz_portal', BASE_DIR = корень репозитория
PROJECT_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = PROJECT_DIR.parent

# Инициализация django-environ
env = environ.Env(
    # Устанавливаем значения по умолчанию для переменных окружения
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
)

# Читаем .env файл из корня проекта
env_path = env.str('ENV_PATH', default=str(BASE_DIR / '.env'))
if os.path.exists(env_path):
    environ.Env.read_env(env_path)

# Базовые настройки безопасности
SECRET_KEY = env.str('SECRET_KEY', default='change-me-in-production')
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.postgres',

    'rest_framework',
    'crispy_forms',
    'crispy_bootstrap5',

    'core',
    'users',
    'issues',
    'articles',
    'submissions',
    'reviews',
]

# Базовый список middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.RedirectMiddleware',  # Обработка редиректов старых URL
]

# WhiteNoise для статических файлов (опционально, только если установлен)
# В продакшене обязателен, в разработке опционален
try:
    import whitenoise
    # Вставляем WhiteNoise после SecurityMiddleware
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
except ImportError:
    # WhiteNoise не установлен - это нормально для разработки
    pass

ROOT_URLCONF = 'jhdkz_portal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'jhdkz_portal.wsgi.application'

# База данных: по умолчанию SQLite для dev, можно переопределить через DATABASE_URL
# В prod.py будет использоваться DATABASE_URL для Postgres
DATABASES = {
    'default': env.db(
        'DATABASE_URL',
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}'
    )
}

LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Asia/Almaty'
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('ru', 'Русский'),
    ('kk', 'Казахский'),
    ('en', 'English'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Статические и медиа файлы
STATIC_URL = 'static/'
STATIC_ROOT = env.str('STATIC_ROOT', default=str(BASE_DIR / 'staticfiles'))
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

MEDIA_URL = 'media/'
MEDIA_ROOT = env.str('MEDIA_ROOT', default=str(BASE_DIR / 'media'))

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Настройки безопасности (базовые, переопределяются в prod.py)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

# Логирование
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': env.str('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
        'etl': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}


