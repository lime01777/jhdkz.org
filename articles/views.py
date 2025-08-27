from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q, Sum, Count
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from .models import Article
from issues.models import Issue

User = get_user_model()

class ArticleListView(ListView):
    """Список статей."""
    model = Article
    template_name = 'articles/article_list.html'
    context_object_name = 'articles'
    paginate_by = 12
    
    def get_queryset(self):
        return Article.objects.filter(status='published').select_related('issue').prefetch_related('authors')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Статистика
        context['total_articles'] = Article.objects.filter(status='published').count()
        context['total_views'] = Article.objects.filter(status='published').aggregate(
            total_views=Sum('views')
        )['total_views'] or 0
        context['total_downloads'] = Article.objects.filter(status='published').aggregate(
            total_downloads=Sum('downloads')
        )['total_downloads'] or 0
        context['total_authors'] = User.objects.filter(role='author').count()
        
        # Годы для фильтрации
        context['years'] = Issue.objects.filter(
            status='published'
        ).values_list('year', flat=True).distinct().order_by('-year')
        
        return context

class ArticleDetailView(DetailView):
    """Детальная страница статьи."""
    model = Article
    template_name = 'articles/article_detail.html'
    context_object_name = 'article'
    
    def get_queryset(self):
        return Article.objects.filter(status='published').select_related('issue').prefetch_related('authors')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Увеличиваем счетчик просмотров
        self.object.increment_views()
        
        # Похожие статьи
        similar_articles = Article.objects.filter(
            status='published'
        ).exclude(
            pk=self.object.pk
        ).filter(
            Q(issue=self.object.issue) | 
            Q(authors__in=self.object.authors.all())
        ).distinct()[:3]
        
        context['similar_articles'] = similar_articles
        return context

def article_search(request):
    """Поиск статей."""
    query = request.GET.get('q', '')
    language = request.GET.get('language', 'ru')
    year = request.GET.get('year', '')
    article_language = request.GET.get('article_language', '')
    
    articles = Article.objects.filter(status='published').select_related('issue').prefetch_related('authors')
    
    if query:
        # Поиск по названию, аннотации и ключевым словам
        if language == 'ru':
            articles = articles.filter(
                Q(title_ru__icontains=query) |
                Q(abstract_ru__icontains=query) |
                Q(keywords_ru__icontains=query)
            )
        elif language == 'kk':
            articles = articles.filter(
                Q(title_kk__icontains=query) |
                Q(abstract_kk__icontains=query) |
                Q(keywords_kk__icontains=query)
            )
        elif language == 'en':
            articles = articles.filter(
                Q(title_en__icontains=query) |
                Q(abstract_en__icontains=query) |
                Q(keywords_en__icontains=query)
            )
        else:
            # Поиск по всем языкам
            articles = articles.filter(
                Q(title_ru__icontains=query) | Q(title_kk__icontains=query) | Q(title_en__icontains=query) |
                Q(abstract_ru__icontains=query) | Q(abstract_kk__icontains=query) | Q(abstract_en__icontains=query) |
                Q(keywords_ru__icontains=query) | Q(keywords_kk__icontains=query) | Q(keywords_en__icontains=query)
            )
    
    # Фильтр по году выпуска
    if year:
        articles = articles.filter(issue__year=year)
    
    # Фильтр по языку статьи
    if article_language:
        articles = articles.filter(language=article_language)
    
    # Сортировка по дате создания
    articles = articles.order_by('-created_at')
    
    # Статистика поиска
    total_views = articles.aggregate(total_views=Sum('views'))['total_views'] or 0
    total_downloads = articles.aggregate(total_downloads=Sum('downloads'))['total_downloads'] or 0
    unique_authors = articles.values('authors').distinct().count()
    
    # Годы для фильтрации
    years = Issue.objects.filter(status='published').values_list('year', flat=True).distinct().order_by('-year')
    
    context = {
        'articles': articles,
        'query': query,
        'language': language,
        'selected_year': year,
        'selected_article_language': article_language,
        'years': years,
        'total_views': total_views,
        'total_downloads': total_downloads,
        'unique_authors': unique_authors,
    }
    
    return render(request, 'articles/article_search.html', context)

def article_download(request, pk):
    """Загрузка PDF статьи."""
    article = get_object_or_404(Article, pk=pk, status='published')
    
    # Увеличиваем счетчик загрузок
    article.increment_downloads()
    
    if article.pdf_file:
        response = HttpResponse(article.pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{article.get_title()}.pdf"'
        return response
    else:
        return HttpResponse("PDF файл не найден", status=404)

def author_articles(request, author_id):
    """Статьи конкретного автора."""
    author = get_object_or_404(User, pk=author_id, role='author')
    articles = Article.objects.filter(
        authors=author,
        status='published'
    ).select_related('issue').prefetch_related('authors').order_by('-created_at')
    
    context = {
        'author': author,
        'articles': articles,
    }
    return render(request, 'articles/author_articles.html', context)
