from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """Форма создания пользователя."""
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'full_name', 'organization', 'orcid', 'role', 'bio')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Настройка полей
        self.fields['username'].help_text = 'Обязательное поле. 150 символов или меньше. Только буквы, цифры и @/./+/-/_'
        self.fields['email'].required = True
        self.fields['full_name'].required = True
        self.fields['role'].initial = 'author'

class CustomUserChangeForm(UserChangeForm):
    """Форма редактирования пользователя."""
    
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('username', 'email', 'full_name', 'organization', 'orcid', 'role', 'bio', 'avatar', 'phone', 'address', 'email_notifications')

class UserProfileForm(forms.ModelForm):
    """Форма профиля пользователя."""
    
    class Meta:
        model = User
        fields = ('full_name', 'email', 'organization', 'orcid', 'bio', 'avatar', 'phone', 'address', 'email_notifications')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Настройка полей
        self.fields['email'].required = True
        self.fields['full_name'].required = True

class AuthorRegistrationForm(UserCreationForm):
    """Форма регистрации автора."""
    
    class Meta:
        model = User
        fields = ('username', 'email', 'full_name', 'organization', 'orcid', 'bio', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Устанавливаем роль автора
        self.fields['role'].initial = 'author'
        self.fields['role'].widget = forms.HiddenInput()
        
        # Настройка полей
        self.fields['email'].required = True
        self.fields['full_name'].required = True
        self.fields['organization'].required = True
        
        # Помощь для полей
        self.fields['orcid'].help_text = 'Формат: 0000-0000-0000-0000'
        self.fields['bio'].widget = forms.Textarea(attrs={'rows': 4})
        
    def clean_orcid(self):
        """Валидация ORCID."""
        orcid = self.cleaned_data.get('orcid')
        if orcid:
            # Простая проверка формата ORCID
            if not orcid.replace('-', '').isdigit() or len(orcid.replace('-', '')) != 16:
                raise forms.ValidationError('ORCID должен быть в формате 0000-0000-0000-0000')
        return orcid 