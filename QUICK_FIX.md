# Быстрое исправление проблем на VPS

## Шаги для исправления

### 1. Создайте/обновите файл `.env` в корне проекта:

```env
DEBUG=False
SECRET_KEY=your-secret-key-change-this
ALLOWED_HOSTS=31.3.209.35,localhost,127.0.0.1
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
CSRF_TRUSTED_ORIGINS=http://31.3.209.35,http://localhost
DATABASE_URL=sqlite:///db.sqlite3
```

### 2. Установите WhiteNoise (для статических файлов):

```bash
pip install whitenoise
```

### 3. Убедитесь, что используете правильные настройки:

Проверьте, что переменная окружения установлена:
```bash
export DJANGO_SETTINGS_MODULE=jhdkz_portal.settings.prod
```

### 4. Соберите статические файлы:

```bash
python manage.py collectstatic --noinput
```

### 5. Перезапустите сервер:

```bash
# Если используете systemd
sudo systemctl restart jhdkz

# Или если запускаете вручную
pkill -f gunicorn
gunicorn jhdkz_portal.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

## Проверка

Откройте в браузере:
- http://31.3.209.35/ - главная страница
- http://31.3.209.35/articles/ - список статей
- http://31.3.209.35/issues/ - список выпусков
- http://31.3.209.35/accounts/login/ - вход
- http://31.3.209.35/users/register/ - регистрация

## Если проблемы остаются

1. Проверьте логи:
```bash
sudo journalctl -u jhdkz -n 50
```

2. Проверьте, что миграции применены:
```bash
python manage.py migrate
```

3. Проверьте, что база данных содержит данные

4. Убедитесь, что DJANGO_SETTINGS_MODULE установлен правильно

