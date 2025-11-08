from django import forms
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Fieldset

from .models import Submission, SubmissionFile, Section, SubmissionAuthor
from users.models import User


class SubmissionForm(forms.ModelForm):
    """Форма для создания/редактирования подачи."""
    
    class Meta:
        model = Submission
        fields = [
            'section', 'title_ru', 'title_kk', 'title_en',
            'abstract_ru', 'abstract_kk', 'abstract_en',
            'keywords_ru', 'keywords_kk', 'keywords_en',
            'language', 'manuscript_file',
        ]
        widgets = {
            'section': forms.Select(attrs={'class': 'form-select'}),
            'title_ru': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'title_kk': forms.TextInput(attrs={'class': 'form-control'}),
            'title_en': forms.TextInput(attrs={'class': 'form-control'}),
            'abstract_ru': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'required': True}),
            'abstract_kk': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'abstract_en': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'keywords_ru': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ключевые слова через запятую'}),
            'keywords_kk': forms.TextInput(attrs={'class': 'form-control'}),
            'keywords_en': forms.TextInput(attrs={'class': 'form-control'}),
            'language': forms.Select(attrs={'class': 'form-select'}),
            'manuscript_file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Основная информация',
                'section',
                Row(
                    Column('title_ru', css_class='form-group col-md-12'),
                ),
                Row(
                    Column('title_kk', css_class='form-group col-md-6'),
                    Column('title_en', css_class='form-group col-md-6'),
                ),
                'language',
            ),
            Fieldset(
                'Аннотация',
                Row(
                    Column('abstract_ru', css_class='form-group col-md-12'),
                ),
                Row(
                    Column('abstract_kk', css_class='form-group col-md-6'),
                    Column('abstract_en', css_class='form-group col-md-6'),
                ),
            ),
            Fieldset(
                'Ключевые слова',
                Row(
                    Column('keywords_ru', css_class='form-group col-md-12'),
                ),
                Row(
                    Column('keywords_kk', css_class='form-group col-md-6'),
                    Column('keywords_en', css_class='form-group col-md-6'),
                ),
            ),
            Fieldset(
                'Рукопись',
                'manuscript_file',
            ),
            Submit('submit', 'Сохранить и продолжить', css_class='btn btn-primary'),
        )
    
    def clean_manuscript_file(self):
        """Валидация файла рукописи."""
        file = self.cleaned_data.get('manuscript_file')
        if not file and not self.instance.pk:
            raise ValidationError('Необходимо загрузить файл рукописи.')
        
        if file:
            # Проверка размера файла (максимум 50 МБ)
            if file.size > 50 * 1024 * 1024:
                raise ValidationError('Размер файла не должен превышать 50 МБ.')
            
            # Проверка расширения
            ext = file.name.split('.')[-1].lower()
            if ext not in ['pdf', 'doc', 'docx']:
                raise ValidationError('Поддерживаются только файлы PDF, DOC и DOCX.')
        
        return file


class SubmissionFileForm(forms.ModelForm):
    """Форма для загрузки дополнительных файлов."""
    
    class Meta:
        model = SubmissionFile
        fields = ['file', 'file_type', 'name', 'description']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'file_type': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название файла (опционально)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Описание файла (опционально)'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'file',
            'file_type',
            'name',
            'description',
            Submit('submit', 'Загрузить файл', css_class='btn btn-primary'),
        )
    
    def clean_file(self):
        """Валидация загружаемого файла."""
        file = self.cleaned_data.get('file')
        if file:
            # Проверка размера
            if file.size > 50 * 1024 * 1024:
                raise ValidationError('Размер файла не должен превышать 50 МБ.')
        return file


class SubmissionMetadataForm(forms.ModelForm):
    """Форма для метаданных подачи."""
    
    class Meta:
        model = Submission
        fields = [
            'research_field', 'methodology', 'funding',
            'ethics_approval', 'ethics_committee',
            'conflict_of_interest', 'data_availability',
            'author_comments',
        ]
        widgets = {
            'research_field': forms.TextInput(attrs={'class': 'form-control'}),
            'methodology': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'funding': forms.TextInput(attrs={'class': 'form-control'}),
            'ethics_approval': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ethics_committee': forms.TextInput(attrs={'class': 'form-control'}),
            'conflict_of_interest': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'data_availability': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'author_comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Любые комментарии для редактора'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Исследовательская информация',
                'research_field',
                'methodology',
                'funding',
            ),
            Fieldset(
                'Этические аспекты',
                Row(
                    Column('ethics_approval', css_class='form-group col-md-12'),
                ),
                'ethics_committee',
                'conflict_of_interest',
                'data_availability',
            ),
            Fieldset(
                'Комментарии',
                'author_comments',
            ),
            Submit('submit', 'Сохранить', css_class='btn btn-primary'),
        )


class SubmissionAuthorForm(forms.ModelForm):
    """Форма для добавления или обновления соавтора подачи."""

    author = forms.ModelChoiceField(
        queryset=User.objects.none(),
        label="Пользователь",
        help_text="Выберите зарегистрированного пользователя, которого нужно добавить как соавтора.",
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    email = forms.EmailField(
        label="Email (для уведомления)",
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = SubmissionAuthor
        fields = [
            'author',
            'author_order',
            'is_corresponding',
            'is_principal',
            'affiliation',
            'orcid',
            'email',
        ]
        widgets = {
            'author_order': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'is_corresponding': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_principal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'affiliation': forms.TextInput(attrs={'class': 'form-control'}),
            'orcid': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0000-0000-0000-0000'}),
        }

    def __init__(self, *args, **kwargs):
        self.submission = kwargs.pop('submission', None)
        super().__init__(*args, **kwargs)
        self.fields['author'].queryset = User.objects.filter(is_active=True).order_by('full_name', 'username')

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.layout = Layout(
            Fieldset(
                'Добавить соавтора',
                Row(
                    Column('author', css_class='form-group col-md-6'),
                    Column('author_order', css_class='form-group col-md-2'),
                    Column('is_principal', css_class='form-group col-md-2 d-flex align-items-center'),
                    Column('is_corresponding', css_class='form-group col-md-2 d-flex align-items-center'),
                ),
                Row(
                    Column('email', css_class='form-group col-md-6'),
                    Column('affiliation', css_class='form-group col-md-6'),
                ),
                'orcid',
            ),
            Submit('submit', 'Добавить автора', css_class='btn btn-primary'),
        )

    def clean_author(self):
        author = self.cleaned_data['author']
        if self.submission and SubmissionAuthor.objects.filter(submission=self.submission, author=author).exists():
            raise ValidationError('Этот пользователь уже добавлен в список авторов.')
        return author

    def clean_is_corresponding(self):
        is_corresponding = self.cleaned_data.get('is_corresponding')
        if (
            is_corresponding
            and self.submission
            and self.submission.submission_authors.filter(is_corresponding=True).exists()
        ):
            raise ValidationError('Корреспондирующий автор уже указан. Снимите чекбокс или обновите текущего автора.')
        return is_corresponding


