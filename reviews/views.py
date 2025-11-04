from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.utils import timezone
from datetime import timedelta

from .models import Review, ReviewAssignment, EditorialDecision
from submissions.models import Submission
from .forms import ReviewAssignmentForm, ReviewForm, EditorialDecisionForm


def is_editor_or_admin(user):
    """Проверка, что пользователь редактор или администратор."""
    return user.is_authenticated and (user.is_editor() or user.is_staff)


@login_required
@user_passes_test(is_editor_or_admin)
def editor_dashboard(request):
    """Редакторская панель."""
    # Статистика
    all_submissions = Submission.objects.all()
    submitted = all_submissions.filter(status='submitted')
    under_review = all_submissions.filter(status__in=['reviewing', 'reviewer_assigned'])
    awaiting_decision = all_submissions.filter(status='review_completed')
    accepted = all_submissions.filter(status='accepted')
    rejected = all_submissions.filter(status='rejected')
    
    # Мои назначенные подачи
    my_submissions = all_submissions.filter(assigned_editor=request.user)
    
    # Просроченные рецензии
    overdue_reviews = ReviewAssignment.objects.filter(
        status__in=['pending', 'accepted'],
        review_due__lt=timezone.now()
    ).select_related('submission', 'reviewer')
    
    context = {
        'submitted_count': submitted.count(),
        'under_review_count': under_review.count(),
        'awaiting_decision_count': awaiting_decision.count(),
        'accepted_count': accepted.count(),
        'rejected_count': rejected.count(),
        'my_submissions': my_submissions[:10],
        'overdue_reviews': overdue_reviews[:10],
    }
    
    return render(request, 'reviews/editor_dashboard.html', context)


@login_required
@user_passes_test(is_editor_or_admin)
def submission_queue(request):
    """Очередь подач для редактора."""
    status_filter = request.GET.get('status', 'all')
    
    submissions = Submission.objects.all()
    
    if status_filter == 'submitted':
        submissions = submissions.filter(status='submitted')
    elif status_filter == 'reviewing':
        submissions = submissions.filter(status__in=['reviewing', 'reviewer_assigned'])
    elif status_filter == 'awaiting_decision':
        submissions = submissions.filter(status='review_completed')
    elif status_filter == 'my_assigned':
        submissions = submissions.filter(assigned_editor=request.user)
    
    submissions = submissions.order_by('-created_at')
    
    return render(request, 'reviews/submission_queue.html', {
        'submissions': submissions,
        'status_filter': status_filter,
    })


@login_required
@user_passes_test(is_editor_or_admin)
def submission_editor_detail(request, pk):
    """Детальный просмотр подачи для редактора."""
    submission = get_object_or_404(Submission, pk=pk)
    
    # Назначение себе при POST запросе
    if request.method == 'POST' and 'assign_to_me' in request.POST:
        submission.assigned_editor = request.user
        submission.save()
        messages.success(request, 'Подача назначена вам.')
        return redirect('reviews:submission_editor_detail', pk=submission.pk)
    
    # Получаем все рецензии и назначения
    reviews = submission.reviews.all()
    assignments = submission.review_assignments.all()
    decisions = submission.editorial_decisions.all()
    
    # Доступные рецензенты
    from users.models import User
    available_reviewers = User.objects.filter(role='reviewer', is_active=True)
    
    context = {
        'submission': submission,
        'reviews': reviews,
        'assignments': assignments,
        'decisions': decisions,
        'available_reviewers': available_reviewers,
    }
    
    return render(request, 'reviews/submission_editor_detail.html', context)


@login_required
@user_passes_test(is_editor_or_admin)
def assign_reviewer(request, submission_pk):
    """Назначение рецензента на статью."""
    submission = get_object_or_404(Submission, pk=submission_pk)
    
    if request.method == 'POST':
        form = ReviewAssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.submission = submission
            assignment.assigned_by = request.user
            assignment.status = 'pending'
            
            # Устанавливаем дедлайны (по умолчанию 14 дней)
            if not assignment.review_due:
                assignment.review_due = timezone.now() + timedelta(days=14)
            
            assignment.save()
            
            # Отправляем email уведомление
            from submissions.utils import send_review_invitation_email
            send_review_invitation_email(assignment)
            
            messages.success(request, f'Рецензент {assignment.reviewer.get_full_name()} назначен на статью.')
            return redirect('reviews:submission_editor_detail', pk=submission.pk)
    else:
        form = ReviewAssignmentForm()
    
    return render(request, 'reviews/assign_reviewer.html', {
        'form': form,
        'submission': submission,
    })


@login_required
def reviewer_dashboard(request):
    """Панель рецензента."""
    assignments = ReviewAssignment.objects.filter(reviewer=request.user).order_by('-assigned_at')
    
    # Статистика
    pending = assignments.filter(status='pending')
    accepted = assignments.filter(status='accepted')
    completed = assignments.filter(status='completed')
    overdue = [a for a in accepted if a.is_overdue()]
    
    return render(request, 'reviews/reviewer_dashboard.html', {
        'assignments': assignments[:20],
        'pending_count': pending.count(),
        'accepted_count': accepted.count(),
        'completed_count': completed.count(),
        'overdue_count': len(overdue),
    })


@login_required
def review_assignment_detail(request, pk):
    """Детальный просмотр назначения рецензии."""
    assignment = get_object_or_404(
        ReviewAssignment,
        pk=pk,
        reviewer=request.user
    )
    
    if request.method == 'POST':
        if 'accept' in request.POST:
            assignment.accept()
            messages.success(request, 'Вы приняли предложение рецензировать статью.')
            
            # Создаем Review объект
            review, created = Review.objects.get_or_create(
                submission=assignment.submission,
                reviewer=assignment.reviewer,
                defaults={
                    'status': 'in_progress',
                    'assignment': assignment,
                }
            )
            assignment.review = review
            assignment.save()
            
            return redirect('reviews:do_review', pk=review.pk)
            
        elif 'decline' in request.POST:
            reason = request.POST.get('decline_reason', '')
            assignment.decline(reason)
            messages.info(request, 'Вы отклонили предложение.')
            return redirect('reviews:reviewer_dashboard')
    
    return render(request, 'reviews/review_assignment_detail.html', {
        'assignment': assignment,
    })


@login_required
def do_review(request, pk):
    """Выполнение рецензии."""
    review = get_object_or_404(
        Review,
        pk=pk,
        reviewer=request.user
    )
    
    if review.status == 'completed':
        messages.info(request, 'Рецензия уже завершена.')
        return redirect('reviews:reviewer_dashboard')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            review = form.save(commit=False)
            review.status = 'completed'
            review.completed_at = timezone.now()
            review.save()
            
            # Обновляем назначение
            if review.assignment:
                review.assignment.status = 'completed'
                review.assignment.save()
            
            # Обновляем статус подачи
            submission = review.submission
            if submission.status == 'reviewer_assigned':
                submission.status = 'review_completed'
            submission.last_review_date = timezone.now()
            submission.save()
            
            # Отправляем email уведомление
            from submissions.utils import send_review_completed_email
            send_review_completed_email(review)
            
            messages.success(request, 'Рецензия успешно отправлена!')
            return redirect('reviews:reviewer_dashboard')
    else:
        form = ReviewForm(instance=review)
    
    return render(request, 'reviews/do_review.html', {
        'review': review,
        'form': form,
        'submission': review.submission,
    })


@login_required
@user_passes_test(is_editor_or_admin)
def make_editorial_decision(request, submission_pk):
    """Принятие редакторского решения."""
    submission = get_object_or_404(Submission, pk=submission_pk)
    
    if request.method == 'POST':
        form = EditorialDecisionForm(request.POST)
        # Устанавливаем queryset для рецензий
        form.fields['reviews'].queryset = submission.reviews.filter(status='completed')
        
        if form.is_valid():
            decision = form.save(commit=False)
            decision.submission = submission
            decision.decision_maker = request.user
            decision.decided_at = timezone.now()
            
            # Определяем, финальное ли это решение
            if decision.decision in ['accept', 'reject']:
                decision.is_final = True
            
            decision.save()
            form.save_m2m()  # Сохраняем связанные рецензии
            
            # Обновляем статус подачи
            decision_map = {
                'accept': 'accepted',
                'revision_minor': 'revision_requested',
                'revision_major': 'revision_requested',
                'resubmit': 'revision_requested',
                'reject': 'rejected',
            }
            new_status = decision_map.get(decision.decision, submission.status)
            submission.status = new_status
            submission.editor_decision_date = timezone.now()
            submission.save()
            
            # Отправляем email уведомление
            from submissions.utils import send_editorial_decision_email
            send_editorial_decision_email(decision)
            
            messages.success(request, f'Решение принято: {decision.get_decision_display_ru()}')
            return redirect('reviews:submission_editor_detail', pk=submission.pk)
    else:
        form = EditorialDecisionForm()
        # Предзаполняем связанные рецензии
        reviews = submission.reviews.filter(status='completed')
        form.fields['reviews'].queryset = reviews
        form.fields['reviews'].initial = reviews
    
    return render(request, 'reviews/make_decision.html', {
        'form': form,
        'submission': submission,
    })
