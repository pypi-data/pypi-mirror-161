from .settings import DJANGO_QUERYSET_DEFAULT_PARAMS
from django.utils.module_loading import import_string


def get_default_params(user=None):
    return import_string(DJANGO_QUERYSET_DEFAULT_PARAMS)(user)