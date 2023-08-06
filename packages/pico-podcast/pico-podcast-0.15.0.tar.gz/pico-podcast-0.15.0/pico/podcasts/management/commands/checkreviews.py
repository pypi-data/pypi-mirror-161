from django.core.management.base import BaseCommand
from django.db import transaction
from pico.podcasts.models import Podcast


class Command(BaseCommand):
    help = 'Check podcast feed directories for new reviews'

    def handle(self, *args, **options):
        for podcast in Podcast.objects.iterator():
            print(podcast)
            with transaction.atomic():
                podcast.check_reviews(
                    lambda review: print('- %s' % review)
                )
