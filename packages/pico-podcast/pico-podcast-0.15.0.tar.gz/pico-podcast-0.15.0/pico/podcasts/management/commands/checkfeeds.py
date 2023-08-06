from django.core.management.base import BaseCommand
from django.db import transaction
from pico.podcasts.models import Podcast


class Command(BaseCommand):
    help = 'Check podcast feeds for new data'

    def handle(self, *args, **options):
        for podcast in Podcast.objects.all():
            print(podcast)
            with transaction.atomic():
                podcast.check_feed(
                    lambda episode: print('- %s' % episode)
                )
