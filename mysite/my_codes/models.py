from django.contrib.auth.models import User
from django.db import models


# Create your models here.


class NIKNEM(models.Model):
    niknem = models.CharField(max_length=30, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.niknem


class Friend(models.Model):
    current_user = models.ForeignKey(User, related_name='owner', on_delete=models.CASCADE, null=True)
    users = models.ManyToManyField(User, related_name='friends')

    # niknem = models.CharField(null=True,max_length=50)

    # def get_niknem(self):
    #     self.niknem = NIKNEM.objects.get(user=self.users.first()).niknem

    @classmethod
    def make_friend(cls, current_user, new_friend):
        friend, created = cls.objects.get_or_create(
            current_user=current_user
        )
        friend.users.add(new_friend)

    @classmethod
    def lose_friend(cls, current_user, friend_to_lose):
        friend, created = cls.objects.get_or_create(
            current_user=current_user
        )
        friend.users.remove(friend_to_lose)

    def __str__(self):
        return self.current_user.username


class Turnir(models.Model):
    date = models.DateField()
    name = models.CharField(max_length=50)
    participants = models.IntegerField()
    placeToWatch = models.CharField(max_length=50)


class Reviews(models.Model):
    id_commentator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_id_commentator')
    id_topic_comm = models.CharField(max_length=20,null=True)
    text_id_comm = models.CharField(max_length=300)
    id_commented = models.ForeignKey(User, on_delete=models.CASCADE, related_name="id_commented", null=True)
