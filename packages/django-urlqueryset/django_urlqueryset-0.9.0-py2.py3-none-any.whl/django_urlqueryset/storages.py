from tempfile import SpooledTemporaryFile

import magic
import requests
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible
from django.utils.functional import LazyObject

from .utils import get_default_params


@deconstructible
class UrlStorage(FileSystemStorage):
    def get_available_name(self, name, *args, **kwargs):
        return name

    def get_params(self):
        params = get_default_params()
        params.pop('fetch_method')
        return params

    def _open(self, url, mode='rb'):
        params = self.get_params()
        params['url'] = url
        file = SpooledTemporaryFile(mode='b')
        file.write(requests.get(**params).content)
        file.seek(0)
        return File(file, mode)

    def _save(self, url, content):
        params = self.get_params()
        params['url'] = url
        params.setdefault('headers', {})['Content-Type'] = magic.from_buffer(content.read(100), mime=True)
        content.seek(0)
        response = requests.post(data=content.read(), **params)
        response.raise_for_status()
        return url

    def save(self, name, content, max_length=None):
        """
        In Django 3.2.11 has been introduced a validation on the file name that can't contain these characters {'', '.', '..'}
        In this package it is used an url as a name file which contains '.'. This raises a SuspiciousFileOperation exception.
        So, this line has been removed validate_file_name(name, allow_relative_path=True) to avoid the exception
        """
        # Get the proper name for the file, as it will actually be saved.
        if name is None:
            name = content.name

        if not hasattr(content, 'chunks'):
            content = File(content, name)

        name = self.get_available_name(name, max_length=max_length)
        name = self._save(name, content)
        return name

    def exists(self, name):
        return True

    def listdir(self, path):
        return [], []

    def url(self, name):
        return name


class DefaultStorage(LazyObject):
    def _setup(self):
        self._wrapped = UrlStorage()


default_storage = DefaultStorage()
