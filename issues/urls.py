from django.urls import path
from . import views

app_name = 'issues'

urlpatterns = [
    # Список выпусков
    path('', views.IssueListView.as_view(), name='issue_list'),
    
    # Архив выпусков
    path('archive/', views.issue_archive, name='issue_archive'),
    
    # Детальная страница выпуска
    path('<int:year>/<int:number>/', views.IssueDetailView.as_view(), name='issue_detail'),
] 