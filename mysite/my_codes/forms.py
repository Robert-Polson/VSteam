from django import forms
from django.forms import CharField


class SearchUserForm(forms.Form):
    query = CharField(required=True, label='')
