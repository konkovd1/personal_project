from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django_countries.fields import CountryField

from eshopper.main.models import Customer

class BootstrapFormMixin:
    fields = {}

    def _init_bootstrap_form_controls(self):
        for _, field in self.fields.items():
            if not hasattr(field.widget, 'attrs'):
                setattr(field.widget, 'attrs', {})
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = ''
            field.widget.attrs['class'] += ' form-control'

class CreateProfileForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
    )
    last_name = forms.CharField(
        max_length=30,
    )

    def clean(self):
        email = self.cleaned_data.get('email')
        if Customer.objects.filter(email=email).exists():
            raise ValidationError("A user with that email already exists.")
        return self.cleaned_data

    def save(self, commit=True):
        user = super().save(commit=commit)

        profile = Customer(
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            email=self.cleaned_data['email'],
            user=user,
        )

        if commit:
            profile.save()
        return user

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name')
        help_texts = {
            'username': None,
            'email': None,
        }
        widgets = {
            'username': forms.TextInput(
                attrs={
                    'placeholder': 'Enter Username',
                }
            ),
            'email': forms.TextInput(
                attrs={
                    'placeholder': 'Enter Email',
                }
            ),
            'password1': forms.TextInput(
                attrs={
                    'placeholder': 'Enter Password',
                }
            ),
            'password2': forms.TextInput(
                attrs={
                    'placeholder': 'Repeat Password',
                }
            ),
            'first_name': forms.TextInput(
                attrs={
                    'placeholder': 'Enter First Name',
                }
            ),
            'last_name': forms.TextInput(
                attrs={
                    'placeholder': 'Enter Last Name',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        self.fields['password1'].widget.attrs.update({'placeholder': 'Enter Password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Repeat Password'})
        self.fields['first_name'].widget.attrs.update({'placeholder': 'Enter First Name'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Enter Last Name'})


class CheckoutForm(forms.Form, BootstrapFormMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_bootstrap_form_controls()

    first_name = forms.CharField(
        max_length=30,
    )

    last_name = forms.CharField(
        max_length=30,
    )

    email = forms.EmailField()

    mobile_phone = forms.CharField(
        max_length=30,
    )

    address = forms.CharField(
        max_length=30,
    )

    country = CountryField(blank_label='(select country)').formfield()

    city = forms.CharField(
        max_length=30,
    )

    zip_code = forms.CharField()