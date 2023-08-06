from .handlers import HandlerBase
from .registry import Library


default_app_config = 'pico.miditags.apps.MiditagsConfig'
tags = Library()


def register(name):
    def wrapper(cls):
        tags.register(name, cls)
        return cls

    return wrapper


__all__ = (
    'HandlerBase',
    'tags',
    'register'
)
