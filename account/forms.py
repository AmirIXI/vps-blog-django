from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class UserRegisterForm(forms.Form):
    username = forms.CharField(max_length=70, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Your Username'}))
    first_name = forms.CharField(required=False, max_length=40, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Your First Name'}))
    last_name = forms.CharField(required=False, max_length=40, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Your Last Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Your Email Address'}))
    password1 = forms.CharField(label='password', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Your Password'}))
    password2 = forms.CharField(label='confirm password', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Your Password'}))

    def clean_username(self):
        username = self.cleaned_data['username']
        user = User.objects.filter(username=username).exists()
        if user:
            raise ValidationError(f'This username ({username}) is already exists')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        user = User.objects.filter(email=email).exists()
        if user:
            raise ValidationError('somthing wrong try again')
        return email

    def clean(self):
        cd = super().clean()
        p1 = cd.get('password1')
        p2 = cd.get('password2')

        if p1 and p2 and p1 != p2:
            raise ValidationError('Passwords must be match !')


class UserLoginForm(forms.Form):
    username = forms.CharField(label='username or email', max_length=70, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Your Username or Email Address'}))
    password = forms.CharField(label='password', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Your Password'}))

