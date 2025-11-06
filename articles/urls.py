from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    # Список статей
    path('', views.ArticleListView.as_view(), name='article_list'),
    
    # Поиск статей
    path('search/', views.article_search, name='article_search'),
    
<<<<<<< HEAD
=======
    # Создание статьи (только для авторов)
    path('create/', views.ArticleCreateView.as_view(), name='article_create'),
    
<<<<<<< HEAD
>>>>>>> bebf4c4 (initial commit)
    # Детальная страница статьи
    path('<int:pk>/', views.ArticleDetailView.as_view(), name='article_detail'),
    
    # Загрузка PDF статьи
    path('<int:pk>/download/', views.article_download, name='article_download'),
=======
    # Детальная страница статьи (по slug или id)
    path('<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('<int:pk>/', views.ArticleDetailView.as_view(), name='article_detail_by_id'),  # Для обратной совместимости
>>>>>>> 84465c9 (Fix function OJS system)
    
    # Статьи автора
    path('author/<int:author_id>/', views.author_articles, name='author_articles'),
] 