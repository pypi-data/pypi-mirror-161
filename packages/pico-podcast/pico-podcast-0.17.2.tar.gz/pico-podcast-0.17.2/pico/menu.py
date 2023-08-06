from django.utils import timezone
from .conf import settings
from .podcasts.models import Podcast, Page, Post


def get_items(request):
    if settings.DOMAINS_OR_SLUGS == 'slugs':
        yield {
            'url': request.build_absolute_uri('/'),
            'text': 'Home'
        }

        for podcast in Podcast.objects.all():
            yield {
                'url': podcast.build_absolute_uri(),
                'text': podcast.short_name or podcast.name
            }

        for page in Page.objects.filter(
            podcast=None,
            menu_visible=True
        ):
            yield {
                'url': page.get_absolute_url(),
                'text': page.menu_title or page.title
            }

        if Post.objects.filter(
            published__lte=timezone.now(),
            podcast=None
        ).exists():
            yield {
                'url': '/blog/',
                'text': 'Blog'
            }

        if settings.CONTACT_FORM:
            yield {
                'url': '/contact/',
                'text': 'Contact'
            }

        return

    for item in request.podcast.get_menu_items():
        yield item


def build(request):
    items = list(get_items(request))

    for item in items:
        if item['url'] == request.path:
            item['active'] = True

        item['url'] = request.build_absolute_uri(item['url'])

    return items
