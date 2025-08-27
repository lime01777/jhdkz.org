from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Регистрация
    path('register/', views.AuthorRegistrationView.as_view(), name='register'),
    
    # Личный кабинет
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.UserProfileUpdateView.as_view(), name='profile'),
    path('my-articles/', views.my_articles, name='my_articles'),
] 