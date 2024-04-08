import os

from django import template

from mysite.settings import MEDIA_URL, MEDIA_ROOT

register = template.Library()


@register.simple_tag(name="user_avatar")
def user_avatar(userid):
    path = MEDIA_ROOT + "/avatars/" + str(userid) + ".png"
    print(MEDIA_ROOT + "/avatars/" + str(userid) + ".png")
    if os.path.isfile(path):
        return MEDIA_URL + "avatars/" + str(userid) + ".png"
    else:
        return MEDIA_URL + "avatars/default.png"
