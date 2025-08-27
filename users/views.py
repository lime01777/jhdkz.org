from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import AuthorRegistrationForm, UserProfileForm
from .models import User

class AuthorRegistrationView(CreateView):
    """Регистрация автора."""
    model = User
    form_class = AuthorRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('core:home')
    
    def form_valid(self, form):
        """Обработка успешной регистрации."""
        user = form.save(commit=False)
        user.role = 'author'  # Устанавливаем роль автора
        user.save()
        
        # Автоматический вход после регистрации
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user)
        
        messages.success(self.request, 'Регистрация успешно завершена! Добро пожаловать в Journal of Health Development!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Обработка ошибок валидации."""
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)

class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля пользователя."""
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')
    
    def get_object(self):
        """Получаем текущего пользователя."""
        return self.request.user
    
    def form_valid(self, form):
        """Обработка успешного обновления."""
        messages.success(self.request, 'Профиль успешно обновлен!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Обработка ошибок валидации."""
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)

@login_required
def dashboard(request):
    """Личный кабинет пользователя."""
    user = request.user
    
    # Статистика пользователя
    if user.role == 'author':
        articles = user.articles.filter(status='published')
        total_articles = articles.count()
        total_views = sum(article.views for article in articles)
        total_downloads = sum(article.downloads for article in articles)
    else:
        total_articles = 0
        total_views = 0
        total_downloads = 0
    
    context = {
        'user': user,
        'total_articles': total_articles,
        'total_views': total_views,
        'total_downloads': total_downloads,
    }
    
    return render(request, 'users/dashboard.html', context)

@login_required
def my_articles(request):
    """Мои статьи (для авторов)."""
    if request.user.role != 'author':
        messages.error(request, 'Эта страница доступна только авторам.')
        return redirect('users:dashboard')
    
    articles = request.user.articles.all().select_related('issue').prefetch_related('authors').order_by('-created_at')
    
    context = {
        'articles': articles,
    }
    
    return render(request, 'users/my_articles.html', context)
