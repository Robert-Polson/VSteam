from django.db import models
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm
# Create your models here.

class Account(models.Model):
    name = models.CharField(max_length=30)
    second_name = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    password = models.CharField(max_length=30)
class NIKNEM(models.Model):
    niknem=models.CharField(max_length=30,null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.niknem
class Avatar(models.Model):
    image = models.ImageField()
    account = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'Avatar for {self.niknem.user.username} ({self.niknem.niknem})'


