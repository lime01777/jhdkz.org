from .base import *  # noqa

DEBUG = True
ALLOWED_HOSTS = ['*']

# Настройки аутентификации для разработки
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'users:dashboard'
LOGOUT_REDIRECT_URL = 'core:home'

# Дополнительные настройки для отладки
if DEBUG:
    # Включаем логирование SQL запросов
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django.db.backends': {
                'level': 'DEBUG',
                'handlers': ['console'],
            },
        },
    }

REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = [  # type: ignore
    'rest_framework.permissions.AllowAny',
]

# Email настройки (для разработки - консольный вывод)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@jhdkz.org'
SERVER_EMAIL = 'server@jhdkz.org'

# В продакшене использовать реальный SMTP:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@gmail.com'
# EMAIL_HOST_PASSWORD = 'your-password'


