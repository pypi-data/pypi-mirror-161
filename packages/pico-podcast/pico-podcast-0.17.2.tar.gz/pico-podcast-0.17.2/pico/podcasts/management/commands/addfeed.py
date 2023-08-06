from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from feedparser import parse
from pico.podcasts.models import Podcast


class Command(BaseCommand):
    help = 'Add a podcast via RSS feed URL'

    def add_arguments(self, parser):
        parser.add_argument('url', type=str)

    def handle(self, *args, **options):
        feed = parse(options['url'])
        exc = feed.get('bozo_exception')

        if exc is not None:
            raise CommandError(
                'That does not appear to be a valid feed.'
            ) from exc

        for link in feed['feed'].get('links', []):
            if link.get('rel') == 'self':
                url = link['href']
                break

        with transaction.atomic():
            for podcast in Podcast.objects.filter(
                rss_feed_url=url
            ):
                return podcast.check_feed(print)

            Podcast.objects.ingest(url, feed, print)
