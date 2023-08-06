from django.template import Library
from .. import tags


register = Library()


@register.filter()
def miditags(value):
    return tags.parse(value)
