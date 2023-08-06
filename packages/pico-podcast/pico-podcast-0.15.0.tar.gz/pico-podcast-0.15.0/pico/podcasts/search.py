from django.utils import html
from markdown import markdown
from watson import search as watson


class EpisodeSearchAdapter(watson.SearchAdapter):
    def get_description(self, obj):
        return obj.summary

    def get_content(self, obj):
        return '\n'.join(
            (
                obj.body and html.strip_tags(markdown(obj.body)) or '',
                ', '.join(
                    obj.categories.values_list('name', flat=True)
                ),
                ', '.join(
                    obj.hosts.values_list('name', flat=True)
                )
            )
        )


class PostSearchAdapter(watson.SearchAdapter):
    def get_description(self, obj):
        return obj.summary

    def get_content(self, obj):
        return '\n'.join(
            (
                obj.body and html.strip_tags(markdown(obj.body)) or '',
                ', '.join(
                    obj.categories.values_list('name', flat=True)
                ),
                str(obj.author)
            )
        )


class PageSearchAdapter(watson.SearchAdapter):
    def get_description(self, obj):
        return ''

    def get_content(self, obj):
        if obj.body:
            return html.strip_tags(markdown(obj.body))

        return ''
