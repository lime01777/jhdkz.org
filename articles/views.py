from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.db import models
from django.db.models import Q, Sum, Count
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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
    """
    Детальная страница статьи.
    Поддерживает поиск по slug или pk.
    Показывает только опубликованные статьи для обычных пользователей.
    Авторы могут видеть свои неопубликованные статьи.
    """
    model = Article
    template_name = 'articles/article_detail.html'
    context_object_name = 'article'
    slug_url_kwarg = 'slug'
    slug_field = 'slug'
    pk_url_kwarg = 'pk'
    
    def get_queryset(self):
        """
        Возвращает queryset статей в зависимости от роли пользователя.
        - Обычные пользователи (неавторизованные или не-авторы): только опубликованные статьи
        - Авторы: опубликованные статьи + свои статьи в любом статусе
        """
        # Базовый queryset с оптимизацией
        base_queryset = Article.objects.select_related('issue', 'section').prefetch_related('authors')
        
        user = self.request.user

        if not user.is_authenticated:
            return base_queryset.filter(status='published')

        # Администраторы/редакторы видят все статьи
        if hasattr(user, 'is_editor') and user.is_editor():
            return base_queryset
        if user.is_staff:
            return base_queryset

        # Авторы видят опубликованные + свои статьи
        if hasattr(user, 'role') and user.role == 'author':
            return base_queryset.filter(
                models.Q(status='published') | models.Q(authors=user)
            ).distinct()

        # Остальные — только опубликованные
        return base_queryset.filter(status='published')
    
    def get_object(self, queryset=None):
        """
        Получает объект статьи по slug или pk из URL.
        Использует get_queryset() для фильтрации только опубликованных статей.
        """
        # Получаем queryset (уже отфильтрованный через get_queryset())
        if queryset is None:
            queryset = self.get_queryset()
        
        # Получаем параметры из URL
        slug = self.kwargs.get(self.slug_url_kwarg)
        pk = self.kwargs.get(self.pk_url_kwarg)
        
        # Ищем по slug (приоритет) или по pk (fallback)
        if slug:
            try:
                obj = queryset.get(slug=slug)
            except Article.DoesNotExist:
                if slug.isdigit():
                    obj = get_object_or_404(queryset, pk=int(slug))
                else:
                    raise
        elif pk:
            obj = get_object_or_404(queryset, pk=pk)
        else:
            # Это не должно произойти при правильной настройке URL
            raise AttributeError(
                f"ArticleDetailView должен получать '{self.slug_url_kwarg}' или '{self.pk_url_kwarg}' в kwargs"
            )
        
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Увеличиваем счетчик просмотров только для опубликованных статей
        if self.object.status == 'published':
            self.object.increment_views()
        
        # Похожие статьи (только опубликованные)
        similar_articles = Article.objects.filter(
            status='published'
        ).exclude(
            pk=self.object.pk
        ).filter(
            Q(issue=self.object.issue) | 
            Q(authors__in=self.object.authors.all())
        ).distinct()[:3]
        
        context['similar_articles'] = similar_articles
        context['can_view_draft'] = (
            self.request.user.is_authenticated and 
            self.request.user.role == 'author' and 
            self.request.user in self.object.authors.all()
        )
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


@login_required
def article_create_redirect(request):
    """Направляем авторов в единый workflow подачи (submissions:create)."""
    if hasattr(request.user, 'role') and request.user.role != 'author' and not request.user.is_staff:
        messages.error(request, 'Создавать подачи могут только авторы.')
        return redirect('users:dashboard')

    messages.info(
        request,
        'Создание статей выполняется через мастер подачи. '
        'Пожалуйста, заполните заявку на публикацию.'
    )
    return redirect('submissions:create')
