from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Account(models.Model):
    name = models.CharField(max_length=30)
    second_name = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    password = models.CharField(max_length=30)

class NIKNEM(models.Model):
    niknem=models.CharField(max_length=30,null=True)
    account=models.ForeignKey(to=Account,on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.niknem
class Avatar(models.Model):
    image = models.ImageField()
    account = models.ForeignKey(to=Account, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'Avatar for {self.account.first_name} {self.account.last_name} ({self.account.nickname})'

class Turnir(models.Model):
    date = models.DateField()
    name = models.CharField()
    participants = models.IntegerField()
    placeToWatch = models.CharField()