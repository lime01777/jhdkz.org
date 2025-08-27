from django.urls import path
from . import views

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
    
    # Статические страницы
    path('<slug:slug>/', views.PageDetailView.as_view(), name='page_detail'),
] 