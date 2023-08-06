from django.core.exceptions import ImproperlyConfigured
import yaml
import os


class Settings(object):
    def __init__(self):
        self.__defaults = {
            'DOMAINS_OR_SLUGS': 'domains',
            'CONTACT_FORM': True
        }

        filename = os.path.join(os.getcwd(), 'settings.yaml')
        if not os.path.exists(filename):
            filename = os.path.join(os.getcwd(), 'settings.yml')

        if not os.path.exists(filename):
            raise ImproperlyConfigured('settings.yaml file not found.')

        with open(filename, 'rb') as stream:
            conf = yaml.load(stream, yaml.SafeLoader)
            if not isinstance(conf, dict):
                raise ImproperlyConfigured(
                    'settings.yaml must contain a set of key-value pairs.'
                )

            self.__conf = conf

    def __getattr__(self, attr):
        return self.__conf.get(
            attr.lower(),
            self.__defaults.get(attr)
        )


settings = Settings()
