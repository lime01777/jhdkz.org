# Инструкция по развертыванию на VPS

## Быстрое исправление проблем

### 1. Создайте файл `.env` в корне проекта

```bash
# Базовые настройки
DEBUG=False
SECRET_KEY=your-secret-key-here-change-in-production

# ALLOWED_HOSTS (обязательно укажите IP вашего сервера)
ALLOWED_HOSTS=31.3.209.35,localhost,127.0.0.1

# База данных (если используете SQLite для начала)
DATABASE_URL=sqlite:///db.sqlite3
# Или PostgreSQL:
# DATABASE_URL=postgres://user:password@localhost:5432/jhdkz_db

# Настройки безопасности для HTTP (если не используете HTTPS)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

# CSRF trusted origins (обязательно укажите ваш домен/IP)
CSRF_TRUSTED_ORIGINS=http://31.3.209.35,http://localhost

# Настройки файлов
STATIC_ROOT=/path/to/your/project/staticfiles
MEDIA_ROOT=/path/to/your/project/media
```

### 2. Установите зависимости

```bash
pip install -r requirements.txt
```

### 3. Убедитесь, что используете правильный файл настроек

Установите переменную окружения:
```bash
export DJANGO_SETTINGS_MODULE=jhdkz_portal.settings.prod
```

Или в systemd сервисе добавьте:
```ini
Environment="DJANGO_SETTINGS_MODULE=jhdkz_portal.settings.prod"
```

### 4. Примените миграции

```bash
python manage.py migrate
```

### 5. Соберите статические файлы

```bash
python manage.py collectstatic --noinput
```

### 6. Создайте суперпользователя (если еще не создан)

```bash
python manage.py createsuperuser
```

### 7. Запустите сервер

#### Вариант 1: Через gunicorn (рекомендуется)

```bash
gunicorn jhdkz_portal.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

#### Вариант 2: Через systemd (для автозапуска)

Создайте файл `/etc/systemd/system/jhdkz.service`:

```ini
[Unit]
Description=Journal of Health Development
After=network.target

[Service]
User=your-user
Group=www-data
WorkingDirectory=/path/to/your/project
Environment="DJANGO_SETTINGS_MODULE=jhdkz_portal.settings.prod"
Environment="PATH=/path/to/your/venv/bin"
ExecStart=/path/to/your/venv/bin/gunicorn jhdkz_portal.wsgi:application --bind 127.0.0.1:8000 --workers 3
Restart=always

[Install]
WantedBy=multi-user.target
```

Затем:
```bash
sudo systemctl daemon-reload
sudo systemctl enable jhdkz
sudo systemctl start jhdkz
sudo systemctl status jhdkz
```

### 8. Настройте Nginx (рекомендуется)

Создайте файл `/etc/nginx/sites-available/jhdkz`:

```nginx
server {
    listen 80;
    server_name 31.3.209.35;

    # Максимальный размер загружаемых файлов
    client_max_body_size 100M;

    # Статические файлы
    location /static/ {
        alias /path/to/your/project/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Медиа файлы
    location /media/ {
        alias /path/to/your/project/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    # Проксирование на Django
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Активируйте конфигурацию:
```bash
sudo ln -s /etc/nginx/sites-available/jhdkz /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Проверка работоспособности

### Проверьте логи

```bash
# Логи gunicorn (если используете systemd)
sudo journalctl -u jhdkz -f

# Логи Django
tail -f /path/to/your/project/logs/django.log

# Логи Nginx
sudo tail -f /var/log/nginx/error.log
```

### Проверьте доступность

```bash
# Проверка основного URL
curl http://31.3.209.35/

# Проверка статических файлов
curl http://31.3.209.35/static/admin/css/base.css

# Проверка статей
curl http://31.3.209.35/articles/

# Проверка выпусков
curl http://31.3.209.35/issues/
```

## Решение проблем

### Проблема: "DisallowedHost" ошибка

**Решение:** Убедитесь, что в `.env` указан правильный `ALLOWED_HOSTS`:
```
ALLOWED_HOSTS=31.3.209.35,localhost,127.0.0.1
```

### Проблема: Статические файлы не загружаются

**Решение:**
1. Убедитесь, что выполнили `python manage.py collectstatic`
2. Проверьте, что WhiteNoise установлен: `pip install whitenoise`
3. Проверьте, что WhiteNoise добавлен в MIDDLEWARE в `base.py`

### Проблема: CSRF ошибка при авторизации/регистрации

**Решение:** Убедитесь, что в `.env` указан `CSRF_TRUSTED_ORIGINS`:
```
CSRF_TRUSTED_ORIGINS=http://31.3.209.35,http://localhost
```

### Проблема: Редирект на HTTPS при использовании HTTP

**Решение:** В `.env` установите:
```
SECURE_SSL_REDIRECT=False
```

### Проблема: Статьи/выпуски не открываются

**Решение:**
1. Проверьте, что база данных содержит данные
2. Проверьте логи на наличие ошибок
3. Убедитесь, что миграции применены: `python manage.py migrate`

### Проблема: Авторизация/регистрация не работает

**Решение:**
1. Проверьте, что `LOGIN_URL` и `LOGIN_REDIRECT_URL` настроены в `prod.py`
2. Проверьте, что CSRF настроен правильно
3. Проверьте логи на наличие ошибок

## Дополнительные настройки

### Включение HTTPS (рекомендуется)

1. Установите certbot:
```bash
sudo apt install certbot python3-certbot-nginx
```

2. Получите сертификат:
```bash
sudo certbot --nginx -d your-domain.com
```

3. Обновите `.env`:
```
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
CSRF_TRUSTED_ORIGINS=https://your-domain.com
```

### Настройка логирования

В `prod.py` можно добавить файловое логирование:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

Не забудьте создать папку `logs`:
```bash
mkdir logs
chmod 755 logs
```

