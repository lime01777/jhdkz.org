PY=python
VENV=venv

.PHONY: help dev etl import test migrate deploy collectstatic

help:
	@echo "Доступные команды:"
	@echo "  make dev        - Запуск сервера разработки"
	@echo "  make etl        - Запуск ETL краулинга"
	@echo "  make import     - Импорт данных из JSONL"
	@echo "  make test       - Запуск тестов"
	@echo "  make migrate    - Применение миграций"
	@echo "  make deploy     - Развертывание (collectstatic + migrate)"

dev:
	$(PY) manage.py runserver

etl:
	$(PY) -m etl crawl --start https://jhdkz.org/ --out data/raw.jsonl --langs ru,kk,en

import:
	$(PY) manage.py import_jhd --source data/raw.jsonl --lang ru,kk,en --since 2010 --dry-run

test:
	$(PY) manage.py test

migrate:
	$(PY) manage.py migrate

collectstatic:
	$(PY) manage.py collectstatic --noinput

deploy: collectstatic migrate
	@echo "Развертывание завершено"

urls:
	$(PY) manage.py show_urls | cat

route-audit:
	$(PY) manage.py route_audit || exit 1

import-redirects:
	$(PY) manage.py import_redirects $(FILE)


