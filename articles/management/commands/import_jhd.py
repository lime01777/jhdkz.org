"""
Management команда для импорта данных из старого OJS сайта.
"""
from __future__ import annotations
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify
from typing import Iterable, Dict, Any
from pathlib import Path
import json
import logging
from issues.models import Issue
from articles.models import Article
from users.models import User
from core.models_extended import RawDocument, Event

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Импорт контента JHD из папки или URL"

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            required=True,
            help="Путь к файлу/папке или URL для скачивания"
        )
        parser.add_argument(
            "--lang",
            default="ru,kk,en",
            help="Языки через запятую"
        )
        parser.add_argument(
            "--since",
            type=int,
            default=2010,
            help="Минимальный год для импорта"
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Только проверка без сохранения в БД"
        )

    def handle(self, *args, **options):
        source = options["source"]
        langs = [l.strip() for l in options["lang"].split(",")]
        since = options["since"]
        dry_run = options["dry_run"]

        self.stdout.write(self.style.SUCCESS(f"Начало импорта из: {source}"))
        if dry_run:
            self.stdout.write(self.style.WARNING("РЕЖИМ ПРОВЕРКИ (dry-run) - изменения не будут сохранены"))

        # Получаем итератор сырых документов
        raw_iter: Iterable[Dict[str, Any]]
        
        if source.startswith("http"):
            # Загружаем через ETL crawler
            from etl.crawler import crawl_site
            self.stdout.write("Загрузка данных через ETL crawler...")
            raw_iter = crawl_site(
                start_url=source,
                langs=langs,
                since_year=since
            )
        else:
            # Читаем из файла
            path = Path(source)
            if not path.exists():
                raise CommandError(f"Файл не найден: {source}")
            
            if path.suffix in {".jsonl", ".json"}:
                if path.suffix == ".jsonl":
                    raw_iter = (
                        json.loads(line)
                        for line in path.read_text(encoding="utf-8").splitlines()
                        if line.strip()
                    )
                else:
                    # JSON файл
                    data = json.loads(path.read_text(encoding="utf-8"))
                    if isinstance(data, list):
                        raw_iter = iter(data)
                    else:
                        raw_iter = iter([data])
            else:
                raise CommandError(f"Неподдерживаемый формат файла: {path.suffix}")

        # Обрабатываем документы
        stats = {
            'processed': 0,
            'imported': 0,
            'skipped': 0,
            'errors': 0,
        }

        try:
            for doc in raw_iter:
                stats['processed'] += 1
                
                try:
                    # Дедупликация по sha256
                    sha256 = doc.get('sha256')
                    if sha256 and not dry_run:
                        exists = RawDocument.objects.filter(sha256=sha256).exists()
                        if exists:
                            stats['skipped'] += 1
                            continue
                    
                    # Парсим документ
                    doc_type = doc.get('doc_type', 'unknown')
                    
                    if doc_type == 'article':
                        self._import_article(doc, dry_run)
                        stats['imported'] += 1
                    elif doc_type == 'issue':
                        self._import_issue(doc, dry_run)
                        stats['imported'] += 1
                    else:
                        stats['skipped'] += 1
                
                except Exception as e:
                    stats['errors'] += 1
                    logger.error(f"Ошибка при обработке документа: {e}")
                    self.stdout.write(self.style.ERROR(f"Ошибка: {e}"))
        
        except Exception as e:
            raise CommandError(f"Критическая ошибка: {e}")

        # Выводим статистику
        self.stdout.write(self.style.SUCCESS("\n=== Статистика ==="))
        self.stdout.write(f"Обработано: {stats['processed']}")
        self.stdout.write(f"Импортировано: {stats['imported']}")
        self.stdout.write(f"Пропущено: {stats['skipped']}")
        self.stdout.write(f"Ошибок: {stats['errors']}")

    def _import_article(self, doc: Dict[str, Any], dry_run: bool):
        """Импортирует статью."""
        # Базовая реализация - нужно доработать под конкретную структуру данных
        data = doc.get('data', {})
        title = data.get('title', 'Untitled')
        
        if not dry_run:
            self.stdout.write(f"Импорт статьи: {title}")
            # TODO: Реализовать полный импорт статьи
        else:
            self.stdout.write(f"[DRY-RUN] Импорт статьи: {title}")

    def _import_issue(self, doc: Dict[str, Any], dry_run: bool):
        """Импортирует выпуск."""
        # Базовая реализация
        if not dry_run:
            self.stdout.write(f"Импорт выпуска")
            # TODO: Реализовать полный импорт выпуска
        else:
            self.stdout.write(f"[DRY-RUN] Импорт выпуска")

