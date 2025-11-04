from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Issue

class IssueListView(ListView):
    """Список выпусков."""
    model = Issue
    template_name = 'issues/issue_list.html'
    context_object_name = 'issues'
    paginate_by = 12
    
    def get_queryset(self):
        return Issue.objects.filter(status='published').prefetch_related('articles')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Группируем выпуски по годам
        issues = self.get_queryset()
        years = {}
        for issue in issues:
            year = issue.year
            if year not in years:
                years[year] = []
            years[year].append(issue)
        
        # Сортируем годы в обратном порядке
        context['years'] = sorted(years.items(), key=lambda x: x[0], reverse=True)
        return context

class IssueDetailView(DetailView):
    """Детальная страница выпуска."""
    model = Issue
    template_name = 'issues/issue_detail.html'
    context_object_name = 'issue'
    
    def get_queryset(self):
        return Issue.objects.filter(status='published').prefetch_related('articles__authors')
    
<<<<<<< HEAD
=======
    def get_object(self, queryset=None):
        """Ищем выпуск по паре year/number из URL вместо pk."""
        queryset = queryset or self.get_queryset()
        year = self.kwargs.get('year')
        number = self.kwargs.get('number')
        return get_object_or_404(queryset, year=year, number=number)
    
>>>>>>> bebf4c4 (initial commit)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем статьи выпуска
        context['articles'] = self.object.articles.filter(status='published').select_related('issue').prefetch_related('authors')
        
        return context

def issue_archive(request):
    """Архив выпусков."""
    year = request.GET.get('year')
    
    issues = Issue.objects.filter(status='published').prefetch_related('articles')
    
    if year:
        issues = issues.filter(year=year)
    
    # Группируем по годам
    years = {}
    for issue in issues:
        year = issue.year
        if year not in years:
            years[year] = []
        years[year].append(issue)
    
    # Сортируем годы в обратном порядке
    grouped_issues = sorted(years.items(), key=lambda x: x[0], reverse=True)
    
    # Получаем список всех лет для фильтрации
    all_years = Issue.objects.filter(status='published').values_list('year', flat=True).distinct().order_by('-year')
    
    context = {
        'years': grouped_issues,
        'all_years': all_years,
        'selected_year': year,
    }
    return render(request, 'issues/issue_archive.html', context)
