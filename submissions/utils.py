"""
Утилиты для системы подач и рецензирования.
Email уведомления и вспомогательные функции.
"""
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


def send_submission_confirmation_email(submission):
    """Отправка email подтверждения получения подачи."""
    if not settings.EMAIL_HOST_USER:
        return  # Email не настроен
    
    subject = f'Подача получена: {submission.submission_id}'
    
    message = f"""
Здравствуйте, {submission.corresponding_author.get_full_name()}!

Ваша статья "{submission.title_ru}" успешно получена редакцией.

ID подачи: {submission.submission_id}
Раздел: {submission.section.title_ru if submission.section else "Не указан"}

Вы можете отслеживать статус вашей подачи в личном кабинете.

С уважением,
Редакция журнала
"""
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
            [submission.corresponding_author.email],
            fail_silently=True,
        )
    except Exception:
        pass  # Игнорируем ошибки email в разработке


def send_review_invitation_email(assignment):
    """Отправка приглашения рецензенту."""
    if not settings.EMAIL_HOST_USER:
        return
    
    subject = f'Приглашение к рецензированию: {assignment.submission.submission_id}'
    
    invitation_msg = f"\nСообщение от редактора:\n{assignment.invitation_message}\n\n" if assignment.invitation_message else ""
    deadline = assignment.review_due.strftime('%d.%m.%Y') if assignment.review_due else 'Не указан'
    
    message = f"""
Здравствуйте, {assignment.reviewer.get_full_name()}!

Вас приглашают провести рецензию статьи:

Название: {assignment.submission.title_ru}
Раздел: {assignment.submission.section.title_ru if assignment.submission.section else "Не указан"}
ID подачи: {assignment.submission.submission_id}

{invitation_msg}Дедлайн: {deadline}

Пожалуйста, примите или отклоните приглашение в вашем личном кабинете.

С уважением,
Редакция журнала
"""
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
            [assignment.reviewer.email],
            fail_silently=True,
        )
    except Exception:
        pass


def send_review_completed_email(review):
    """Отправка уведомления о завершении рецензии."""
    if not settings.EMAIL_HOST_USER:
        return
    
    # Редактору
    subject = f'Рецензия завершена: {review.submission.submission_id}'
    message = f"""
Рецензия для подачи {review.submission.submission_id} была завершена рецензентом {review.reviewer.get_full_name()}.

Рекомендация: {review.get_recommendation_display()}

Пожалуйста, просмотрите рецензию и примите решение.
"""
    
    try:
        if review.submission.assigned_editor:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
                [review.submission.assigned_editor.email],
                fail_silently=True,
            )
    except Exception:
        pass


def send_editorial_decision_email(decision):
    """Отправка уведомления об editorial decision."""
    if not settings.EMAIL_HOST_USER:
        return
    
    subject = f'Решение по вашей статье: {decision.submission.submission_id}'
    
    decision_text = decision.get_decision_display_ru()
    
    comments = f"\nКомментарии редактора:\n{decision.comments_for_author}\n" if decision.comments_for_author else ""
    
    message = f"""Здравствуйте, {decision.submission.corresponding_author.get_full_name()}!

По вашей статье "{decision.submission.title_ru}" (ID: {decision.submission.submission_id}) принято решение:

{decision_text}
{comments}
Вы можете просмотреть детали в вашем личном кабинете.

С уважением,
Редакция журнала"""
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
            [decision.submission.corresponding_author.email],
            fail_silently=True,
        )
    except Exception:
        pass

