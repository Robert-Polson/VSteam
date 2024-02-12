from django.db import models

# Create your models here.

class Account(models.Model):
    name = models.CharField(max_length=30)
    second_name = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    password = models.CharField(max_length=30)
class NIKNEM(models.Model):
    niknem=models.CharField(max_length=30,null=True)
