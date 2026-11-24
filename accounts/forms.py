"""
Формы приложения accounts (Темы 6, 7): регистрация, вход, профиль,
восстановление пароля. Вся серверная валидация — здесь.
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = User.ROLE_USER  # роль назначается только по умолчанию
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Имя пользователя или Email',
        widget=forms.TextInput(attrs={'autofocus': True}),
    )

    def confirm_login_allowed(self, user):
        # Разрешаем вход и по email, и по username: если username не найден,
        # Django сам подставит email в authenticate через AUTHENTICATION_BACKENDS.
        super().confirm_login_allowed(user)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('full_name', 'email')
        labels = {'full_name': 'ФИО', 'email': 'Email'}

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Этот email уже занят другим пользователем.')
        return email


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label='Введите ваш Email')


class ResetPasswordForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput, label='Новый пароль',
        help_text='Минимум 8 символов, не только цифры.',
    )
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Подтвердите пароль')

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('confirm_password'):
            raise forms.ValidationError('Пароли не совпадают.')
        return cleaned_data
