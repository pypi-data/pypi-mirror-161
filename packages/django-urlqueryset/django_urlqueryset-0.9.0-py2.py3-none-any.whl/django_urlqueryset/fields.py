from django.db import models
from django.db.models.fields import files as file_fields

from .storages import default_storage
from .utils import get_default_params


class FieldFileMixin:
    def save(self, name, content, save=False):
        return super().save(name, content, save)


class FileFieldMixin:
    def generate_filename(self, instance, filename):
        url = getattr(instance, 'URL', None)
        if not url:
            params = get_default_params()
            url = params["url"].replace("{{model._meta.model_name}}", instance._meta.model_name)
        return f'{url}{instance.pk}/{self.name}/'


class UrlFieldFile(FieldFileMixin, file_fields.FieldFile):
    pass


class UrlImageFieldFile(FieldFileMixin, file_fields.ImageFieldFile):
    pass


class UrlFileField(FileFieldMixin, models.FileField):
    attr_class = UrlFieldFile

    def __init__(self, verbose_name=None, name=None, upload_to='', storage=None, **kwargs):
        storage = storage or default_storage
        super().__init__(verbose_name=verbose_name, name=name, upload_to=upload_to, storage=storage, **kwargs)


class UrlImageField(FileFieldMixin, models.ImageField):
    attr_class = UrlImageFieldFile

    def __init__(self, verbose_name=None, name=None, width_field=None, height_field=None, **kwargs):
        kwargs['storage'] = kwargs.get('storage') or default_storage
        super().__init__(verbose_name=verbose_name, name=name, width_field=width_field, height_field=height_field, **kwargs)