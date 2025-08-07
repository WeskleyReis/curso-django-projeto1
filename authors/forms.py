import re

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


def strong_password(password):
    regex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9]).{8,}$')

    if not regex.match(password):
        raise ValidationError((
            'Password must have at least one uppercase latter, '
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
    
    password2 = forms.CharField(
        label='Confirm Password*',
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Repeat your password',
        }),
        error_messages={
            'required': 'Password must not be empty'
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
            'username': 'Username*',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'E-mail*',
            'password': 'Password*',
        }
        help_texts = {
            'username': '',
        }
        error_messages = {
            'username':{
                'required': 'This field must not be empty.',
                'invalid': 'This field is invalid.',
            },
            'password':{
                'max_lenght': 'The password is very short.'
            }
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Ex.: John',
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Ex.: Doe',
            }),
            'username': forms.TextInput(attrs={
                'placeholder': 'Type your username here',
            }),
            'email': forms.TextInput(attrs={
                'placeholder': 'Type your e-mail here',
            }),
            'password': forms.PasswordInput(attrs={
                'placeholder': 'Type your password here',
            }),
        }
    
    def clean_email(self):
        data = self.cleaned_data.get('email')
        try:
            email = User.objects.get(email=data).first().email
        except:
            email = None

        if data == email:
            raise ValidationError(
                'Email already registered'
            )
        return data
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')

        if password != password2:
            raise ValidationError({
                'password2': 'The passwords do not match',
            })