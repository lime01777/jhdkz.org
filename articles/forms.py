from django import forms
from django.contrib.auth import get_user_model
from .models import Article
from issues.models import Issue

User = get_user_model()

class ArticleCreateForm(forms.ModelForm):
    """Форма для создания статьи автором."""
    
    class Meta:
        model = Article
        fields = [
            'title_ru', 'title_kk', 'title_en',
            'abstract_ru', 'abstract_kk', 'abstract_en', 
            'keywords_ru', 'keywords_kk', 'keywords_en',
            'page_start', 'page_end', 'language', 'pdf_file'
        ]
        widgets = {
            'title_ru': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название статьи на русском языке'
            }),
            'title_kk': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название статьи на казахском языке (необязательно)'
            }),
            'title_en': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название статьи на английском языке (необязательно)'
            }),
            'abstract_ru': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Введите аннотацию статьи на русском языке'
            }),
            'abstract_kk': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Введите аннотацию статьи на казахском языке (необязательно)'
            }),
            'abstract_en': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Введите аннотацию статьи на английском языке (необязательно)'
            }),
            'keywords_ru': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ключевые слова через запятую на русском языке'
            }),
            'keywords_kk': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ключевые слова через запятую на казахском языке (необязательно)'
            }),
            'keywords_en': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ключевые слова через запятую на английском языке (необязательно)'
            }),
            'page_start': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Начальная страница'
            }),
            'page_end': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Конечная страница'
            }),
            'language': forms.Select(attrs={
                'class': 'form-select'
            }),
            'pdf_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем поля обязательными
        self.fields['title_ru'].required = True
        self.fields['abstract_ru'].required = True
        self.fields['keywords_ru'].required = True
        self.fields['page_start'].required = True
        self.fields['page_end'].required = True
        self.fields['pdf_file'].required = True
        
        # Добавляем валидацию
        self.fields['page_end'].widget.attrs['min'] = 1
        self.fields['page_start'].widget.attrs['min'] = 1
    
    def clean(self):
        cleaned_data = super().clean()
        page_start = cleaned_data.get('page_start')
        page_end = cleaned_data.get('page_end')
        
        if page_start and page_end:
            if page_start >= page_end:
                raise forms.ValidationError('Страница начала должна быть меньше страницы конца.')
        
        return cleaned_data
