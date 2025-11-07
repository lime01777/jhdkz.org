"""
Настройки для продакшена (production).
Включает все необходимые настройки безопасности и оптимизации.
"""
from .base import *  # noqa

DEBUG = False

# ALLOWED_HOSTS - обязательно добавить IP или домен сервера
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['31.3.209.35', 'localhost', '127.0.0.1'])

# База данных из DATABASE_URL (Postgres)
DATABASES = {
    'default': env.db('DATABASE_URL')
}

# Настройки безопасности
# ВАЖНО: Если сайт работает по HTTP, установите SECURE_SSL_REDIRECT = False
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False)
# Если используете HTTPS, раскомментируйте:
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_HSTS_SECONDS = 31536000  # 1 год
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# Для HTTP отключаем безопасные cookies
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=False)
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=False)

# Доверенные источники для CSRF - обязательно добавить домен/IP сервера
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[
    'http://31.3.209.35',
    'http://localhost',
])

# Content Security Policy (базовый)
CSP_DEFAULT_SRC = ["'self'"]
CSP_SCRIPT_SRC = ["'self'", "'unsafe-inline'"]  # Для совместимости, можно ужесточить
CSP_STYLE_SRC = ["'self'", "'unsafe-inline'"]
CSP_IMG_SRC = ["'self'", "data:", "https:"]
CSP_FONT_SRC = ["'self'", "https:"]

# Настройки для статических файлов в продакшене
# WhiteNoise для обслуживания статических файлов (установлен в requirements.txt)
# Убедитесь, что 'whitenoise.middleware.WhiteNoiseMiddleware' добавлен в MIDDLEWARE в base.py
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Настройки аутентификации
LOGIN_URL = 'login'  # Используем стандартный URL Django для логина
LOGIN_REDIRECT_URL = 'users:dashboard'  # Редирект после успешного входа
LOGOUT_REDIRECT_URL = 'core:home'  # Редирект после выхода

# Email настройки (должны быть настроены в .env)
EMAIL_BACKEND = env.str('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = env.str('EMAIL_HOST', default='')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env.str('DEFAULT_FROM_EMAIL', default='noreply@jhdkz.org')
SERVER_EMAIL = env.str('SERVER_EMAIL', default='server@jhdkz.org')

# Sentry (если настроен)
SENTRY_DSN = env.str('SENTRY_DSN', default='')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,
    )


