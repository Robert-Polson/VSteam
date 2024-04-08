from django import forms
from django.forms import CharField
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from my_codes.models import Post1


class SearchUserForm(forms.Form):
    query = CharField(required=True, label="Username")


class RememberPassword(forms.Form):
    username = forms.CharField(label="Username")
    email = forms.CharField(label="Login")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")


class LoginForm(forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")


class RegisterForm(UserCreationForm):
    error_messages = {
        "required": "This field is required",
        "invalid": "Enter a valid email address",
    }

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error("password2", ("The two password fields didn’t match."))
        return password2


class PostForm(forms.ModelForm):
    class Meta:
        model = Post1
        fields = ["title", "text", "image"]
        labels = {
            "title": "Write a topic",
            "text": "Write a text",
            "image": "Load a picture/video",
        }
