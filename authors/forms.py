import re

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


def strong_password(password):
    regex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9]).{8,}$')

    if not regex.match(password):
        raise ValidationError((
            'Password must have at least one uppercase letter, '
            'one lowercase letter and one number. '
            'The length should be at least 8 characters.'
        ),
            code='Invalid'
        )


class RegisterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['password'].validators = [strong_password]

    username = forms.CharField(
        label='Username*',
        required=True,
        help_text='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Type your username here'
        }),
        min_length=4,
        max_length=150,
        error_messages={
            'required': 'This field must not be empty.',
            'invalid': 'This field is invalid.',
            'min_length': 'The username must have a minimum of 4 characters.',
            'max_length': 'The username must have a maximum of 150 characters.',
        }
    )
    
    password2 = forms.CharField(
        label='Confirm Password*',
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Repeat your password',
        }),
        error_messages={
            'required': 'Password must not be empty.'
        },
    )

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
            'password',
        )
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'E-mail*',
            'password': 'Password*',
        }
        help_texts = {
            'username': '',
        }
        error_messages = {
            'email':{
                'required':'This field must not be empty.',
            },
            'password':{
                'required':'Password must not be empty.',
                'max_length': 'The password is very short.',
            }
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Ex.: John',
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Ex.: Doe',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Type your e-mail here',
            }),
            'password': forms.PasswordInput(attrs={
                'placeholder': 'Type your password here',
            }),
        }
    
    def clean_email(self):
        data = self.cleaned_data.get('email')

        if User.objects.filter(email=data).exists():
            raise ValidationError('Email already registered')
        
        return data
 
    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')

        if password and password2 and password != password2:
            raise ValidationError('The passwords do not match')

        return password2
