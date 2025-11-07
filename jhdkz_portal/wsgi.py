"""
WSGI config for jhdkz_portal project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Для продакшена используйте: jhdkz_portal.settings.prod
# Можно переопределить через переменную окружения: DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jhdkz_portal.settings.prod')

application = get_wsgi_application()
