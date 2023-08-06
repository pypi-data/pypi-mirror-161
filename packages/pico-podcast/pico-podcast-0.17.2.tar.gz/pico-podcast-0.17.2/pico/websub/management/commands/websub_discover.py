from django.core.management.base import BaseCommand
from ...models import Subscription


class Command(BaseCommand):
    help = 'Discover and subscribe to a topic via WebSub'

    def add_arguments(self, parser):
        parser.add_argument('url', type=str)

    def handle(self, *args, **options):
        obj = Subscription.objects.discover(
            options['url']
        )

        obj.subscribe()
        print(obj)
