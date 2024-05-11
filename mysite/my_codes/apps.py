"""for apps"""
from django.apps import AppConfig


class MyCodesConfig(AppConfig):
    """Class that work with my codes config"""
    default_auto_field = "django.db.models.BigAutoField"
    name = "my_codes"
