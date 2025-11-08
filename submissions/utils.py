"""
Утилиты для системы подач и рецензирования.
Email уведомления и вспомогательные функции.
"""
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db import transaction

from articles.models import Article
from issues.models import Issue

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


@transaction.atomic
def publish_submission_to_article(submission):
    """
    Создает или обновляет Article из принятой подачи.
    Возвращает Article или None, если публикация невозможна.
    """
    if submission is None:
        return None

    # Ищем подходящий выпуск (последний по году/номеру)
    issue = Issue.objects.order_by('-year', '-number').first()
    if issue is None:
        return None

    article = Article.objects.filter(submission=submission).first()
    created = False
    if article is None:
        article = Article(submission=submission)
        created = True

    article.issue = issue
    article.section = submission.section
    article.language = submission.language or 'ru'

    article.title_ru = submission.title_ru or submission.title_en or submission.title_kk or 'Без названия'
    article.title_kk = submission.title_kk
    article.title_en = submission.title_en
    article.abstract_ru = submission.abstract_ru
    article.abstract_kk = submission.abstract_kk
    article.abstract_en = submission.abstract_en
    article.keywords_ru = submission.keywords_ru or ''
    article.keywords_kk = submission.keywords_kk or ''
    article.keywords_en = submission.keywords_en or ''

    # Технические поля: минимальные значения, если не заполнены
    article.page_start = article.page_start or 1
    article.page_end = article.page_end or (article.page_start + 1)
    if article.page_end <= article.page_start:
        article.page_end = article.page_start + 1

    if submission.manuscript_file and (created or not article.pdf_file):
        article.pdf_file = submission.manuscript_file

    article.status = 'published'
    article.submitted_at = submission.submitted_at or timezone.now()
    article.published_at = timezone.now()
    article.save()

    # Привязка авторов (корреспондирующий + соавторы)
    authors = []
    if submission.corresponding_author:
        authors.append(submission.corresponding_author)
    authors.extend(list(submission.co_authors.all()))
    if authors:
        article.authors.set(authors)

    return article

