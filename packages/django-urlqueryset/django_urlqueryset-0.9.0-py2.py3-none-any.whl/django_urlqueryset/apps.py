import logging
from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger('django_urlqueryset')


class CheckConfig(AppConfig):
    name = 'django_urlqueryset'

    def ready(self):
        if not self.check_settings():
            raise ImproperlyConfigured(_('django_urlqueryset is not '
                                         'configured correctly. '
                                         'Please check your settings.'))
        self.set_default_settings()

    def check_settings(self):

        return all([
            hasattr(settings, 'URLQS_HIGH_MARK'),
            hasattr(settings, 'URLQS_COUNT'),
            hasattr(settings, 'URLQS_RESULTS'),
        ])

    def set_default_settings(self):
        if not hasattr(settings, 'URLQS_HIGH_MARK'):
            setattr(settings, 'URLQS_HIGH_MARK', 1000000)
        if not hasattr(settings, 'URLQS_COUNT'):
            setattr(settings, 'URLQS_COUNT', 'count')
        if not hasattr(settings, 'URLQS_RESULTS'):
            setattr(settings, 'URLQS_RESULTS', 'results')


