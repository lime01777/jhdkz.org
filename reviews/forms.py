from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Fieldset

from .models import ReviewAssignment, Review, EditorialDecision
from users.models import User


class ReviewAssignmentForm(forms.ModelForm):
    """Форма назначения рецензента."""
    
    reviewer = forms.ModelChoiceField(
        queryset=User.objects.filter(role='reviewer', is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Рецензент",
        help_text="Выберите рецензента для этой статьи"
    )
    
    class Meta:
        model = ReviewAssignment
        fields = ['reviewer', 'review_due', 'invitation_message', 'is_blind', 'can_view_identity']
        widgets = {
            'review_due': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control',
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'invitation_message': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 5,
                    'placeholder': 'Персональное сообщение для рецензента (опционально)'
                }
            ),
            'is_blind': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_view_identity': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'reviewer',
            'review_due',
            'invitation_message',
            Row(
                Column('is_blind', css_class='form-check'),
                Column('can_view_identity', css_class='form-check'),
            ),
            Submit('submit', 'Назначить рецензента', css_class='btn btn-primary'),
        )


class ReviewForm(forms.ModelForm):
    """Форма для выполнения рецензии."""
    
    class Meta:
        model = Review
        fields = [
            # Оценки
            'originality', 'scientific_value', 'methodology', 'presentation',
            'language_quality', 'relevance',
            # Комментарии
            'comments_for_author', 'comments_for_editor', 'general_comments',
            'strengths', 'weaknesses', 'suggestions',
            # Рекомендация
            'recommendation',
            # Файлы
            'review_file', 'annotated_manuscript',
            # Дополнительно
            'time_spent', 'conflict_of_interest', 'conflict_details',
        ]
        widgets = {
            'originality': forms.Select(attrs={'class': 'form-select'}),
            'scientific_value': forms.Select(attrs={'class': 'form-select'}),
            'methodology': forms.Select(attrs={'class': 'form-select'}),
            'presentation': forms.Select(attrs={'class': 'form-select'}),
            'language_quality': forms.Select(attrs={'class': 'form-select'}),
            'relevance': forms.Select(attrs={'class': 'form-select'}),
            'comments_for_author': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'comments_for_editor': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'general_comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'strengths': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'weaknesses': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'suggestions': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'recommendation': forms.Select(attrs={'class': 'form-select'}),
            'review_file': forms.FileInput(attrs={'class': 'form-control'}),
            'annotated_manuscript': forms.FileInput(attrs={'class': 'form-control'}),
            'time_spent': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Минуты'}),
            'conflict_of_interest': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'conflict_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Оценки (по шкале 1-5)',
                Row(
                    Column('originality', css_class='form-group col-md-6'),
                    Column('scientific_value', css_class='form-group col-md-6'),
                ),
                Row(
                    Column('methodology', css_class='form-group col-md-6'),
                    Column('presentation', css_class='form-group col-md-6'),
                ),
                Row(
                    Column('language_quality', css_class='form-group col-md-6'),
                    Column('relevance', css_class='form-group col-md-6'),
                ),
            ),
            Fieldset(
                'Комментарии для автора',
                'comments_for_author',
                'strengths',
                'weaknesses',
                'suggestions',
            ),
            Fieldset(
                'Комментарии для редактора',
                'comments_for_editor',
                'general_comments',
            ),
            Fieldset(
                'Рекомендация',
                'recommendation',
            ),
            Fieldset(
                'Файлы',
                'review_file',
                'annotated_manuscript',
            ),
            Fieldset(
                'Дополнительная информация',
                'time_spent',
                'conflict_of_interest',
                'conflict_details',
            ),
            Submit('submit', 'Отправить рецензию', css_class='btn btn-success btn-lg'),
        )


class EditorialDecisionForm(forms.ModelForm):
    """Форма редакторского решения."""
    
    class Meta:
        model = EditorialDecision
        fields = ['decision', 'comments', 'comments_for_author', 'internal_notes', 'reviews']
        widgets = {
            'decision': forms.Select(attrs={'class': 'form-select'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'comments_for_author': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'internal_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'reviews': forms.CheckboxSelectMultiple(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reviews'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['reviews'].queryset = Review.objects.none()  # Будет заполнено в view
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'decision',
            'comments_for_author',
            'comments',
            'internal_notes',
            'reviews',
            Submit('submit', 'Принять решение', css_class='btn btn-primary btn-lg'),
        )

