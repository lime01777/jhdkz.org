"""
Краулер для сбора данных со старого OJS сайта.
"""
import time
import logging
from typing import Iterator, Dict, Any, Optional, List
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from .util import calculate_sha256, normalize_url, save_jsonl
from .normalize import clean_html

logger = logging.getLogger('etl')


class OJSCrawler:
    """Краулер для OJS сайта."""
    
    def __init__(
        self,
        start_url: str,
        rate_limit: float = 1.0,
        max_pages: Optional[int] = None,
        langs: List[str] = None,
        since_year: int = 2010
    ):
        """
        Инициализация краулера.
        
        Args:
            start_url: Начальный URL для сканирования
            rate_limit: Задержка между запросами в секундах
            max_pages: Максимальное количество страниц для сканирования
            langs: Список языков для обработки (ru, kk, en)
            since_year: Минимальный год для обработки
        """
        self.start_url = start_url.rstrip('/')
        self.rate_limit = rate_limit
        self.max_pages = max_pages
        self.langs = langs or ['ru', 'kk', 'en']
        self.since_year = since_year
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; JHDKZ ETL/1.0)'
        })
        self.visited = set()
        self.pages_processed = 0
    
    def crawl(self, output_path: Optional[str] = None) -> Iterator[Dict[str, Any]]:
        """
        Запускает краулинг сайта.
        
        Yields:
            Словари с данными страниц
        """
        logger.info(f"Начало краулинга: {self.start_url}")
        
        # Обрабатываем основные разделы
        urls_to_process = [
            f"{self.start_url}/index.php/jhd/issue/archive",
            f"{self.start_url}/index.php/jhd/issue/view/",
        ]
        
        for url in urls_to_process:
            if self.max_pages and self.pages_processed >= self.max_pages:
                break
            
            try:
                yield from self._process_url(url)
            except Exception as e:
                logger.error(f"Ошибка при обработке {url}: {e}")
        
        logger.info(f"Краулинг завершен. Обработано страниц: {self.pages_processed}")
    
    def _process_url(self, url: str) -> Iterator[Dict[str, Any]]:
        """Обрабатывает одну URL."""
        if url in self.visited:
            return
        
        if self.max_pages and self.pages_processed >= self.max_pages:
            return
        
        self.visited.add(url)
        self.pages_processed += 1
        
        try:
            time.sleep(self.rate_limit)
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            content = response.content
            sha256 = calculate_sha256(content)
            
            soup = BeautifulSoup(content, 'lxml')
            
            # Определяем тип страницы
            if '/article/view/' in url:
                doc_type = 'article'
                data = self._extract_article(soup, url)
            elif '/issue/view/' in url or '/issue/archive' in url:
                doc_type = 'issue'
                data = self._extract_issue(soup, url)
            else:
                doc_type = 'unknown'
                data = {}
            
            result = {
                'source_url': url,
                'sha256': sha256,
                'doc_type': doc_type,
                'data': data,
                'fetched_at': time.time(),
            }
            
            yield result
            
        except Exception as e:
            logger.error(f"Ошибка при обработке {url}: {e}")
    
    def _extract_article(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Извлекает данные статьи."""
        # Базовая реализация - нужно доработать под конкретную структуру OJS
        title = soup.find('h1') or soup.find('title')
        title_text = title.get_text(strip=True) if title else ''
        
        return {
            'title': title_text,
            'html_content': str(soup),
        }
    
    def _extract_issue(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Извлекает данные выпуска."""
        # Базовая реализация
        return {
            'html_content': str(soup),
        }


def crawl_site(
    start_url: str,
    langs: List[str] = None,
    since_year: int = 2010,
    rate_limit: float = 1.0,
    output_path: Optional[str] = None
) -> Iterator[Dict[str, Any]]:
    """
    Функция для запуска краулинга.
    
    Args:
        start_url: Начальный URL
        langs: Список языков
        since_year: Минимальный год
        rate_limit: Задержка между запросами
        output_path: Путь для сохранения результатов (JSONL)
    
    Yields:
        Словари с данными
    """
    crawler = OJSCrawler(
        start_url=start_url,
        rate_limit=rate_limit,
        langs=langs or ['ru', 'kk', 'en'],
        since_year=since_year
    )
    
    for item in crawler.crawl(output_path):
        if output_path:
            from pathlib import Path
            from .util import save_jsonl
            save_jsonl(item, Path(output_path))
        yield item

