import json
from urllib import parse

import requests
from django.core import serializers
from django.db import models
from django.utils.module_loading import import_string

from .utils import get_default_params


class UrlModel(models.Model):
    class Meta:
        abstract = True

    def get_params(self):
        params = get_default_params()
        params.pop('fetch_method', None)
        objects = type(self).objects
        if 'url' in objects.request_params:
            params.update(objects.request_params.copy())
        return params

    def to_dict(self):
        serializer_name = 'update_serializer' if self.pk else 'create_serializer'
        if hasattr(self, serializer_name):
            serializer = import_string(getattr(self, serializer_name))
            _dict = serializer(instance=self).data
        else:
            _dict = json.loads(serializers.serialize('json', [self]))[0]['fields']

        for field in self._meta.get_fields():
            if isinstance(field, models.FileField):
                _dict.pop(field.name)
        return _dict

    def save(self, *args, **kwargs):
        params = self.get_params()
        data = self.to_dict()
        for k, v in kwargs.items():
            if k in data and isinstance(data[k], dict):
                assert isinstance(v, dict), f"{v} is not a dictionary"
                data[k].update(v)
            else:
                data[k] = v
        if self.pk is None:
            response = requests.post(json=data, **params)
            response.raise_for_status()
        else:
            params['url'] = parse.urljoin(params['url'], f"{self.pk}/")
            response = requests.patch(json=data, **params)
            response.raise_for_status()
        return list(type(self).objects.deserialize(json_data=[response.json()]))[0]

