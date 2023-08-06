from django.conf import settings
from django.template import Library
from django.utils.safestring import mark_safe
from markdown import markdown as md


register = Library()


@register.filter()
def markdown(value, style='default'):
    kwargs = settings.MARKDOWN_STYLES.get(style, {})
    kwargs.update(
        {
            'output_format': 'html'
        }
    )

    if value and str(value).strip():
        return mark_safe(
            md(
                str(value),
                **kwargs
            )
        )

    return ''
