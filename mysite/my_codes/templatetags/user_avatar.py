from django import template
from django.contrib.auth.models import User

from mysite.settings import MEDIA_URL, MEDIA_ROOT
from my_codes.models import Avatar

register = template.Library()


@register.simple_tag(name='user_avatar')
def user_avatar(userid):
    user = User.objects.get(id=userid)
    try:
        avatar = Avatar.objects.get(user=user)
        return avatar.image.url
    except Avatar.DoesNotExist:
        return MEDIA_URL + 'avatars/default.png'
