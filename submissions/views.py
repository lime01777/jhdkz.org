from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Submission, Section, SubmissionFile, SubmissionAuthor
from .forms import SubmissionForm, SubmissionFileForm, SubmissionMetadataForm


class SubmissionListView(ListView):
    """Список всех подач для автора."""
    model = Submission
    template_name = 'submissions/submission_list.html'
    context_object_name = 'submissions'
    paginate_by = 10
    
    def get_queryset(self):
        """Показываем только подачи текущего пользователя."""
        if self.request.user.is_authenticated:
            return Submission.objects.filter(
                corresponding_author=self.request.user
            ).order_by('-created_at')
        return Submission.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_submissions'] = self.get_queryset().count()
        context['draft_count'] = self.get_queryset().filter(status='draft').count()
        context['submitted_count'] = self.get_queryset().filter(status='submitted').count()
        context['under_review_count'] = self.get_queryset().filter(
            status__in=['reviewing', 'reviewer_assigned']
        ).count()
        return context


@login_required
def submission_create(request):
    """Создание новой подачи (Step 1)."""
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.corresponding_author = request.user
            submission.status = 'draft'
            submission.save()
            form.save_m2m()  # Сохраняем соавторов
            
            messages.success(request, 'Подача создана. Продолжите заполнение.')
            return redirect('submissions:step2', pk=submission.pk)
    else:
        form = SubmissionForm()
    
    sections = Section.objects.filter(is_active=True).order_by('order')
    return render(request, 'submissions/submission_create.html', {
        'form': form,
        'sections': sections,
    })


@login_required
def submission_step2(request, pk):
    """Шаг 2: Загрузка файлов."""
    submission = get_object_or_404(
        Submission, 
        pk=pk, 
        corresponding_author=request.user
    )
    
    if request.method == 'POST':
        form = SubmissionFileForm(request.POST, request.FILES)
        if form.is_valid():
            file_obj = form.save(commit=False)
            file_obj.submission = submission
            file_obj.uploaded_by = request.user
            if not file_obj.name:
                file_obj.name = request.FILES['file'].name
            file_obj.save()
            messages.success(request, 'Файл успешно загружен.')
            return redirect('submissions:step2', pk=submission.pk)
    else:
        form = SubmissionFileForm()
    
    files = submission.files.all()
    return render(request, 'submissions/submission_step2.html', {
        'submission': submission,
        'form': form,
        'files': files,
    })


@login_required
def submission_step3(request, pk):
    """Шаг 3: Добавление авторов."""
    submission = get_object_or_404(
        Submission,
        pk=pk,
        corresponding_author=request.user
    )
    
    # Логика добавления авторов будет реализована через форму
    authors = submission.submission_authors.all()
    
    if request.method == 'POST':
        # Обработка добавления авторов
        pass
    
    return render(request, 'submissions/submission_step3.html', {
        'submission': submission,
        'authors': authors,
    })


@login_required
def submission_step4(request, pk):
    """Шаг 4: Метаданные и дополнительные поля."""
    submission = get_object_or_404(
        Submission,
        pk=pk,
        corresponding_author=request.user
    )
    
    if request.method == 'POST':
        form = SubmissionMetadataForm(request.POST, instance=submission)
        if form.is_valid():
            form.save()
            messages.success(request, 'Метаданные сохранены.')
            return redirect('submissions:step5', pk=submission.pk)
    else:
        form = SubmissionMetadataForm(instance=submission)
    
    return render(request, 'submissions/submission_step4.html', {
        'submission': submission,
        'form': form,
    })


@login_required
def submission_step5(request, pk):
    """Шаг 5: Предварительный просмотр и отправка."""
    submission = get_object_or_404(
        Submission,
        pk=pk,
        corresponding_author=request.user
    )
    
    if request.method == 'POST' and 'submit' in request.POST:
        # Валидация перед отправкой
        if not submission.can_be_submitted():
            messages.error(request, 'Не все обязательные поля заполнены.')
            return redirect('submissions:step5', pk=submission.pk)
        
        # Отправка
        submission.status = 'submitted'
        submission.submitted_at = timezone.now()
        submission.save()
        
        # Отправляем email уведомление
        from .utils import send_submission_confirmation_email
        send_submission_confirmation_email(submission)
        
        messages.success(request, 
            f'Статья успешно отправлена! ID подачи: {submission.submission_id}')
        return redirect('submissions:detail', pk=submission.pk)
    
    # Проверка готовности к отправке
    can_submit = submission.can_be_submitted()
    issues = []
    if not submission.title_ru:
        issues.append('Не указано название статьи')
    if not submission.abstract_ru:
        issues.append('Не заполнена аннотация')
    if not submission.section:
        issues.append('Не выбран раздел')
    if not submission.manuscript_file and not submission.files.exists():
        issues.append('Не загружена рукопись')
    
    return render(request, 'submissions/submission_step5.html', {
        'submission': submission,
        'can_submit': can_submit,
        'issues': issues,
    })


class SubmissionDetailView(DetailView):
    """Детальный просмотр подачи."""
    model = Submission
    template_name = 'submissions/submission_detail.html'
    context_object_name = 'submission'
    
    def get_queryset(self):
        """Разрешаем доступ только автору или редакторам."""
        if self.request.user.is_authenticated:
            if self.request.user.is_editor() or self.request.user.is_staff:
                return Submission.objects.all()
            return Submission.objects.filter(corresponding_author=self.request.user)
        return Submission.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        submission = self.object
        
        # Рецензии
        context['reviews'] = submission.reviews.filter(visible_to_author=True)
        
        # Назначения рецензентов
        context['review_assignments'] = submission.review_assignments.all()
        
        # Редакторские решения
        context['editorial_decisions'] = submission.editorial_decisions.all()
        
        # Файлы
        context['files'] = submission.files.all()
        
        # Авторы
        context['authors'] = submission.submission_authors.all()
        
        return context


@login_required
def submission_withdraw(request, pk):
    """Отзыв подачи автором."""
    submission = get_object_or_404(
        Submission,
        pk=pk,
        corresponding_author=request.user
    )
    
    if submission.status in ['published', 'declined']:
        messages.error(request, 'Нельзя отозвать эту подачу.')
        return redirect('submissions:detail', pk=submission.pk)
    
    if request.method == 'POST':
        submission.status = 'declined'
        submission.save()
        messages.success(request, 'Подача отозвана.')
        return redirect('submissions:list')
    
    return render(request, 'submissions/submission_withdraw.html', {
        'submission': submission,
    })
