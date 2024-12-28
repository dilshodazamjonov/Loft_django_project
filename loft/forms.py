from django import forms
from .models import Category, ShippingAddress
from django_svg_image_form_field import SvgAndImageFormField
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude = []
        field_classes = {
            'icon': SvgAndImageFormField
        }

# Форма для Авторизации
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'contact__section-input'
    }))

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'contact__section-input'
    }))


class RegisterForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'contact__section-input'
    }))

    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'contact__section-input'
    }))

    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'contact__section-input'
    }))

    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'contact__section-input'
    }))

    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'contact__section-input'
    }))

    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'contact__section-input'
    }))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')




class ShippingForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ('address', 'phone', 'region', 'city', 'comment')
        widgets = {
            'address': forms.TextInput(attrs={
                'class': 'contact__section-input',
                'placeholder': 'Ваш адрес (ул. дом. кв)'
            }),

            'phone': forms.TextInput(attrs={
                'class': 'contact__section-input',
                'placeholder': 'Номер телефона'
            }),

            'region': forms.Select(attrs={
                'class': 'contact__section-input',
            }),

            'city': forms.Select(attrs={
                'class': 'contact__section-input',
            }),

            'comment': forms.Textarea(attrs={
                'class': 'contact__section-input',
                'placeholder': 'Комментарий к заказу'
            })

        }





