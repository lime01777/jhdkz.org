from django import template


register = template.Library()


SUBMISSION_STATUS_CLASSES = {
    'draft': 'secondary',
    'submitted': 'primary',
    'reviewing': 'info',
    'reviewer_assigned': 'info',
    'review_completed': 'warning',
    'revision_requested': 'warning',
    'revision_submitted': 'primary',
    'accepted': 'success',
    'in_editing': 'secondary',
    'in_production': 'secondary',
    'scheduled': 'secondary',
    'published': 'success',
    'rejected': 'danger',
    'declined': 'danger',
}

ASSIGNMENT_STATUS_CLASSES = {
    'pending': 'warning',
    'accepted': 'primary',
    'declined': 'secondary',
    'completed': 'success',
    'cancelled': 'secondary',
}


@register.filter
def submission_status_badge(status):
    """Возвращает bootstrap-класс для статуса подачи."""
    if hasattr(status, 'lower'):
        status = status.lower()
    return SUBMISSION_STATUS_CLASSES.get(status, 'secondary')


@register.filter
def assignment_status_badge(status):
    """Возвращает bootstrap-класс для статуса назначения рецензента."""
    if hasattr(status, 'lower'):
        status = status.lower()
    return ASSIGNMENT_STATUS_CLASSES.get(status, 'secondary')

