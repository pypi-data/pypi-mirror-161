from django.core.management.base import BaseCommand
from ...models import Subscription


class Command(BaseCommand):
    help = 'Renew WebSub subscriptions'

    def handle(self, *args, **options):
        for obj in Subscription.objects.iterator():
            obj.subscribe()
            print(obj)
