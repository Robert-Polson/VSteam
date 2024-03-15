from django import forms
from django.forms import CharField
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
class SearchUserForm(forms.Form):
    query = CharField(required=True, label='')

class RememberPassword(forms.Form):
    username=forms.CharField(label='Username')
    email = forms.CharField(label='Login')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
class LoginForm(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')


class RegisterForm(UserCreationForm):
    error_messages = {
        'required': 'This field is required',
        'invalid': 'Enter a valid email address',
    }

    class Meta:
        model=User
        fields = ['username','email','password1','password2']