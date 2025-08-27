from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.db.models import Sum, Count, Q
from .models import SiteSettings, News, Page
from issues.models import Issue
from articles.models import Article
from users.models import User

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
    template_name = 'core/news/news_list.html'
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
    template_name = 'core/news/news_detail.html'
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
