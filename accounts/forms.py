from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm

class LoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)

class SignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username','email',)