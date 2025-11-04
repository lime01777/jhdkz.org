from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Sum, Count, Q
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from .models import SiteSettings, News, Page
from issues.models import Issue
from articles.models import Article
from users.models import User
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db import connection

def home(request):
    """Главная страница."""
    # Получаем статистику
    total_articles = Article.objects.filter(status='published').count()
    total_authors = User.objects.filter(role='author').count()
    total_views = Article.objects.filter(status='published').aggregate(total=Sum('views'))['total'] or 0
    total_downloads = Article.objects.filter(status='published').aggregate(total=Sum('downloads'))['total'] or 0
    
    # Последние статьи
    latest_articles = Article.objects.filter(status='published').select_related('issue').prefetch_related('authors').order_by('-created_at')[:6]
    
    # Последние выпуски
    latest_issues = Issue.objects.filter(status='published').order_by('-published_at')[:3]
    
    # Рекомендуемые новости
    featured_news = News.objects.filter(is_published=True, is_featured=True).order_by('-published_at')[:3]
    
    context = {
        'total_articles': total_articles,
        'total_authors': total_authors,
        'total_views': total_views,
        'total_downloads': total_downloads,
        'latest_articles': latest_articles,
        'latest_issues': latest_issues,
        'featured_news': featured_news,
    }
    
    return render(request, 'core/home.html', context)

def about(request):
    """Страница 'О журнале'."""
    return render(request, 'core/about.html')

def contact(request):
    """Страница контактов."""
    if request.method == 'POST':
        # Обработка формы контактов
        messages.success(request, 'Ваше сообщение успешно отправлено! Мы свяжемся с вами в ближайшее время.')
        return redirect('core:contact')
    
    return render(request, 'core/contact.html')

class NewsListView(ListView):
    """Список новостей."""
    model = News
    template_name = 'core/news_list.html'
    context_object_name = 'news_list'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = News.objects.filter(is_published=True).order_by('-published_at')
        
        # Фильтр по рекомендуемым
        featured = self.request.GET.get('featured')
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_news'] = News.objects.filter(is_published=True, is_featured=True).order_by('-published_at')[:3]
        return context

class NewsDetailView(DetailView):
    """Детальная страница новости."""
    model = News
    template_name = 'core/news_detail.html'
    context_object_name = 'news'
    
    def get_queryset(self):
        return News.objects.filter(is_published=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Похожие новости
        current_news = self.get_object()
        related_news = News.objects.filter(
            is_published=True
        ).exclude(
            id=current_news.id
        ).order_by('-published_at')[:3]
        
        # Рекомендуемые новости
        featured_news = News.objects.filter(
            is_published=True, 
            is_featured=True
        ).exclude(
            id=current_news.id
        ).order_by('-published_at')[:3]
        
        context['related_news'] = related_news
        context['featured_news'] = featured_news
        return context

class PageDetailView(DetailView):
    """Детальная страница статической страницы."""
    model = Page
    template_name = 'core/page_detail.html'
    context_object_name = 'page'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Page.objects.filter(is_published=True)


def author_detail(request, slug):
    """Страница автора. TODO: заменить slug на поле модели пользователя, если появится.
    Временная реализация: slug трактуем как username.
    """
    author = get_object_or_404(User, username=slug)
    articles = author.articles.filter(status='published').select_related('issue').prefetch_related('authors')
    return render(request, 'authors/detail.html', {"author": author, "articles": articles})


def file_download(request, pk):
    """Заглушка скачивания файла по pk. Возвращает 404 до появления модели File.
    """
    return HttpResponse("Файл не найден", status=404)


def robots_txt(request):
    """Отдаёт robots.txt как шаблон."""
    return render(request, 'robots.txt', content_type='text/plain')


def healthz(request):
    """Простой healthcheck endpoint для мониторинга."""
    return JsonResponse({"status": "ok"})


def search_page(request):
    """Страница поиска. Использует простую строку q и шаблон core/search.html."""
    q = request.GET.get('q', '')
    results = []
    if q:
        # Простой fallback-поиск для dev (SQLite): icontains по нескольким моделям
        articles_qs = Article.objects.filter(
            Q(title_ru__icontains=q) | Q(abstract_ru__icontains=q)
        )[:20]
        news_qs = News.objects.filter(Q(title__icontains=q) | Q(content__icontains=q))[:20]
        results.extend([
            {"type": "article", "title": a.get_title('ru'), "url": f"/articles/{a.pk}/"}
            for a in articles_qs
        ])
        results.extend([
            {"type": "news", "title": n.title, "url": f"/news/{n.slug}/"}
            for n in news_qs
        ])
    return render(request, 'core/search.html', {"query": q, "results": results})


def api_search(request):
    """API поиска. Если доступен Postgres, используем tsvector, иначе icontains.
    Возвращает JSON {type, title, url, snippet}.
    """
    q = request.GET.get('q', '')
    items = []
    if not q:
        return JsonResponse({"results": items})

    is_postgres = connection.vendor == 'postgresql'

    if is_postgres:
        try:
            # Полнотекстовый поиск по статьям: заголовки и аннотация RU
            vector = SearchVector('title_ru', weight='A') + SearchVector('abstract_ru', weight='B')
            query = SearchQuery(q)
            art = (
                Article.objects.annotate(rank=SearchRank(vector, query))
                .filter(rank__gte=0.1, status='published')
                .order_by('-rank')[:20]
            )
            for a in art:
                items.append({
                    "type": "article",
                    "title": a.get_title('ru'),
                    "url": f"/articles/{a.pk}/",
                    "snippet": a.get_abstract('ru')[:200]
                })
        except Exception:
            # Fallback на icontains
            pass

    if not items:
        # Fallback: icontains статьи и новости
        for a in Article.objects.filter(
            Q(title_ru__icontains=q) | Q(abstract_ru__icontains=q), status='published'
        )[:20]:
            items.append({
                "type": "article",
                "title": a.get_title('ru'),
                "url": f"/articles/{a.pk}/",
                "snippet": a.get_abstract('ru')[:200]
            })
        for n in News.objects.filter(Q(title__icontains=q) | Q(content__icontains=q))[:20]:
            items.append({
                "type": "news",
                "title": n.title,
                "url": f"/news/{n.slug}/",
                "snippet": (n.excerpt or n.content)[:200]
            })

    return JsonResponse({"results": items})
