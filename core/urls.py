from django.urls import path
from django.contrib.sitemaps import views as sitemap_views
from . import views
from .sitemaps import SITEMAPS

app_name = 'core'

urlpatterns = [
    # Главная страница
    path('', views.home, name='home'),
    
    # О журнале
    path('about/', views.about, name='about'),
    
    # Контакты
    path('contact/', views.contact, name='contact'),
    
    # Новости
    path('news/', views.NewsListView.as_view(), name='news_list'),
    path('news/<slug:slug>/', views.NewsDetailView.as_view(), name='news_detail'),

    # Авторы
    path('authors/<slug:slug>/', views.author_detail, name='author_detail'),

    # Файлы
    path('files/<int:pk>/download/', views.file_download, name='file_download'),

    # Поиск
    path('search/', views.search_page, name='search'),
    path('api/search', views.api_search, name='api_search'),

    # Sitemap и robots
    path('sitemap.xml', sitemap_views.sitemap, {"sitemaps": SITEMAPS}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', views.robots_txt, name='robots_txt'),

    # Healthcheck
    path('healthz', views.healthz, name='healthz'),
    
    # Статические страницы
    path('<slug:slug>/', views.PageDetailView.as_view(), name='page_detail'),
]
