from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.db import models
from django.db.models import Q, Sum, Count
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Article
from .forms import ArticleCreateForm
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
        
        # Если пользователь авторизован и является автором
        if self.request.user.is_authenticated and hasattr(self.request.user, 'role') and self.request.user.role == 'author':
            # Показываем опубликованные статьи ИЛИ статьи автора в любом статусе
            return base_queryset.filter(
                models.Q(status='published') | 
                models.Q(authors=self.request.user)
            ).distinct()
        else:
            # Для всех остальных показываем ТОЛЬКО опубликованные статьи
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
            obj = get_object_or_404(queryset, slug=slug)
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


class ArticleCreateView(LoginRequiredMixin, CreateView):
    """Создание новой статьи автором."""
    model = Article
    form_class = ArticleCreateForm
    template_name = 'articles/article_create.html'
    success_url = reverse_lazy('users:my_articles')
    
    def dispatch(self, request, *args, **kwargs):
        """Проверяем, что пользователь является автором."""
        if not request.user.is_authenticated:
            messages.error(request, 'Необходимо войти в систему.')
            return redirect('login')
        
        if request.user.role != 'author':
            messages.error(request, 'Создавать статьи могут только авторы.')
            return redirect('users:dashboard')
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Обработка успешного создания статьи."""
        # Получаем последний опубликованный выпуск
        try:
            latest_issue = Issue.objects.filter(status='published').order_by('-year', '-number').first()
            if not latest_issue:
                messages.error(self.request, 'Нет доступных выпусков для публикации статьи.')
                return self.form_invalid(form)
            
            # Сохраняем статью
            article = form.save(commit=False)
            article.issue = latest_issue
            article.status = 'draft'  # Статья создается как черновик
            article.save()
            
            # Добавляем автора
            article.authors.add(self.request.user)
            
            messages.success(self.request, 'Статья успешно создана! Она сохранена как черновик.')
            return super().form_valid(form)
            
        except Exception as e:
            messages.error(self.request, f'Ошибка при создании статьи: {str(e)}')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """Обработка ошибок валидации."""
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)
