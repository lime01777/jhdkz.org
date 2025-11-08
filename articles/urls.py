from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    # Список статей
    path('', views.ArticleListView.as_view(), name='article_list'),
    
    # Поиск статей
    path('search/', views.article_search, name='article_search'),
    
    # Создание статьи перенаправляет на workflow подачи
    path('create/', views.article_create_redirect, name='article_create'),
    
    # Статьи автора (должно быть перед детальными страницами)
    path('author/<int:author_id>/', views.author_articles, name='author_articles'),
    
    # Загрузка PDF статьи (должно быть перед детальными страницами)
    path('<int:pk>/download/', views.article_download, name='article_download'),
    
    # Детальная страница статьи (по slug - приоритет, SEO-friendly)
    path('<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
    
    # Детальная страница статьи по pk (fallback для обратной совместимости)
    # ВАЖНО: должен быть после slug, так как иначе будет перехватывать все числовые пути
    path('<int:pk>/', views.ArticleDetailView.as_view(), name='article_detail_by_id'),
]
