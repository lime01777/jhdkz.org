"""
Утилиты для ETL процесса.
"""
import hashlib
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from urllib.parse import urlparse, urljoin

logger = logging.getLogger('etl')


def calculate_sha256(content: bytes) -> str:
    """Вычисляет SHA256 хеш контента."""
    return hashlib.sha256(content).hexdigest()


def normalize_url(url: str, base_url: Optional[str] = None) -> str:
    """Нормализует URL."""
    if base_url:
        return urljoin(base_url, url)
    return url


def save_jsonl(data: Dict[str, Any], output_path: Path) -> None:
    """Сохраняет данные в JSONL файл."""
    with open(output_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False) + '\n')


def load_jsonl(input_path: Path):
    """Загружает данные из JSONL файла."""
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def ensure_dir(path: Path) -> None:
    """Создает директорию если не существует."""
    path.mkdir(parents=True, exist_ok=True)

