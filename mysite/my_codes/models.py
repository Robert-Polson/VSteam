from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class NIKNEM(models.Model):
    niknem = models.CharField(max_length=30, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.niknem
