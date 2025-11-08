from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    # Редакторская панель
    path('editor/dashboard/', views.editor_dashboard, name='editor_dashboard'),
    path('editor/queue/', views.submission_queue, name='submission_queue'),
    path('editor/assignments/', views.reviewer_management, name='reviewer_management'),
    path('editor/issues/create/', views.issue_create, name='issue_create'),
    path('editor/submission/<int:pk>/', views.submission_editor_detail, name='submission_editor_detail'),
    path('editor/submission/<int:submission_pk>/assign-reviewer/', views.assign_reviewer, name='assign_reviewer'),
    path('editor/submission/<int:submission_pk>/decision/', views.make_editorial_decision, name='make_decision'),
    
    # Панель рецензента
    path('reviewer/dashboard/', views.reviewer_dashboard, name='reviewer_dashboard'),
    path('reviewer/assignment/<int:pk>/', views.review_assignment_detail, name='review_assignment_detail'),
    path('reviewer/review/<int:pk>/', views.do_review, name='do_review'),
]

