"""File with models for every page"""
import os
import uuid
from io import BytesIO

from django.contrib.auth.models import User
from django.db import models
from PIL import UnidentifiedImageError, Image


# Create your models here.


class NIKNEM(models.Model):
    """Class that work with nickname of user"""
    objects = None
    niknem = models.CharField(max_length=30, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.niknem


class Friend(models.Model):
    """Class that work with friends of user"""
    objects = None
    current_user = models.ForeignKey(
        User, related_name="owner", on_delete=models.CASCADE, null=True
    )
    users = models.ManyToManyField(User, related_name="friends")

    # nickname = models.CharField(null=True,max_length=50)

    # def get_nickname(self):
    #     self.nickname = nickname.objects.get(user=self.users.first()).nickname

    @classmethod
    def make_friend(cls, current_user, new_friend):
        """Function to make friends"""
        friend, created = cls.objects.get_or_create(current_user=current_user)
        friend.users.add(new_friend)

    @classmethod
    def lose_friend(cls, current_user, friend_to_lose):
        """Function to lose friends"""
        friend, created = cls.objects.get_or_create(current_user=current_user)
        friend.users.remove(friend_to_lose)

    def __str__(self):
        return self.current_user.username

    @classmethod
    def get_friends(cls, current_user):
        """Function to get friends"""
        friend, created = cls.objects.get_or_create(current_user=current_user)
        return friend.users


class Turnir(models.Model):
    """Class that work with turnirs"""
    objects = None
    date = models.DateField()
    name = models.CharField(max_length=50)
    prize = models.CharField(max_length=50)


class Reviews(models.Model):
    """Class that work with reviews"""
    objects = None
    id_commentator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_id_commentator')
    id_topic_comm = models.CharField(max_length=20, null=True)
    text_id_comm = models.CharField(max_length=300)
    id_commented = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="id_commented", null=True)


class Post1(models.Model):
    """Class that work with posts"""
    objects = None
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=65)
    text = models.CharField(max_length=150)
    date = models.DateField(blank="true", auto_now_add=True)

    def __str__(self):
        return self.title


class PostFile(models.Model):
    post = models.ForeignKey(Post1, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    file = models.FileField(upload_to="post_files")
    is_image = models.BooleanField(default=False)

    @staticmethod
    def save_file(post: Post1, file):
        name = file.name
        file.name = str(uuid.uuid4())

        try:
            with BytesIO(file.read()) as f:
                image_handle = Image.open(f)
                image_handle.verify()
                is_image = True
        except Exception:
            is_image = False

        post_model = PostFile(
            post=post,
            name=name,
            file=file,
            is_image=is_image
        )

        post_model.save()


class Likes:
    """Class that work with likes for user"""
    other_user_id_likes = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.IntegerField(blank=True, default="0")


class Comm:
    """Class that work with comments"""
    other_user_id_comm = models.ForeignKey(User, on_delete=models.CASCADE)
    comm = models.IntegerField(blank=True, default="0")


class Avatar(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE, related_name="avatar")
    image = models.ImageField(upload_to="avatars", default="avatars/default.png")

    @staticmethod
    def save_avatar(user: User, image):
        with BytesIO(image.read()) as f:
            image_handle = Image.open(f)
            image_handle.verify()

            image.name = str(user.id) + "-" + str(uuid.uuid4())

            try:
                avatar = Avatar.objects.get(user=user)
                default_value = Avatar._meta.get_field("image").get_default()
                if avatar.image != default_value:
                    os.remove(avatar.image.path)

                avatar.image = None
                avatar.save()
                avatar.image = image
                avatar.save()
            except Avatar.DoesNotExist:
                avatar = Avatar()
                avatar.user = user
                avatar.image = image
                avatar.save()


class Message(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    text = models.CharField(max_length=4096)
    timestamp = models.DateTimeField(auto_now_add=True)


class Socials(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    link_vk = models.CharField(max_length=100, null=True)
    link_youtube = models.CharField(max_length=100, null=True)
    link_discord = models.CharField(max_length=100, null=True)


class Achievement(models.Model):
    author_achievement = models.ForeignKey(User , on_delete=models.CASCADE)
    achievements = models.CharField(max_length=100 , null=True)
