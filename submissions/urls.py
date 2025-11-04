from django.urls import path
from . import views

app_name = 'submissions'

urlpatterns = [
    # Список подач
    path('', views.SubmissionListView.as_view(), name='list'),
    
    # Создание новой подачи
    path('create/', views.submission_create, name='create'),
    
    # Step-by-step процесс подачи
    path('<int:pk>/step2/', views.submission_step2, name='step2'),
    path('<int:pk>/step3/', views.submission_step3, name='step3'),
    path('<int:pk>/step4/', views.submission_step4, name='step4'),
    path('<int:pk>/step5/', views.submission_step5, name='step5'),
    
    # Детальный просмотр
    path('<int:pk>/', views.SubmissionDetailView.as_view(), name='detail'),
    
    # Отзыв подачи
    path('<int:pk>/withdraw/', views.submission_withdraw, name='withdraw'),
]

