from django.apps import AppConfig, apps
from imp import find_module
from importlib import import_module


class MiditagsConfig(AppConfig):
    name = 'pico.miditags'

    def ready(self):
        for config in apps.get_app_configs():
            if config.name == self.name:
                continue

            name = '%s.miditags' % config.name

            try:
                import_module(name)
            except ImportError as ex:
                try:
                    find_module(name)
                except ImportError:
                    continue

                raise ex
