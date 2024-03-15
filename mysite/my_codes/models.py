from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db import models

from mysite import settings

from mysite.settings import MEDIA_ROOT


# Create your models here.

class Account(models.Model):
    name = models.CharField(max_length=30)
    second_name = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    password = models.CharField(max_length=30)


class NIKNEM(models.Model):
    niknem = models.CharField(max_length=30, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.niknem
