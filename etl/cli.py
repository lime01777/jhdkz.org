"""
CLI интерфейс для ETL пакета.
"""
import argparse
import logging
import sys
from pathlib import Path
from typing import List
from .crawler import crawl_site

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('etl')


def main():
    """Главная функция CLI."""
    parser = argparse.ArgumentParser(description='ETL инструменты для импорта данных OJS')
    subparsers = parser.add_subparsers(dest='command', help='Команда')
    
    # Команда crawl
    crawl_parser = subparsers.add_parser('crawl', help='Краулинг сайта')
    crawl_parser.add_argument('--start', required=True, help='Начальный URL')
    crawl_parser.add_argument('--out', required=True, help='Путь к выходному файлу (JSONL)')
    crawl_parser.add_argument('--langs', default='ru,kk,en', help='Языки через запятую')
    crawl_parser.add_argument('--since', type=int, default=2010, help='Минимальный год')
    crawl_parser.add_argument('--rate-limit', type=float, default=1.0, help='Задержка между запросами')
    crawl_parser.add_argument('--max-pages', type=int, help='Максимальное количество страниц')
    
    # Команда import-xml
    xml_parser = subparsers.add_parser('import-xml', help='Импорт из OJS XML')
    xml_parser.add_argument('--zip', required=True, help='Путь к ZIP архиву с экспортом')
    xml_parser.add_argument('--out', required=True, help='Путь к выходному файлу (JSONL)')
    
    args = parser.parse_args()
    
    if args.command == 'crawl':
        langs = [l.strip() for l in args.langs.split(',')]
        output_path = Path(args.out)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Начало краулинга: {args.start}")
        
        count = 0
        for item in crawl_site(
            start_url=args.start,
            langs=langs,
            since_year=args.since,
            rate_limit=args.rate_limit,
            output_path=str(output_path)
        ):
            count += 1
            if args.max_pages and count >= args.max_pages:
                break
        
        logger.info(f"Обработано документов: {count}")
        
    elif args.command == 'import-xml':
        logger.error("Импорт XML пока не реализован")
        sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()

