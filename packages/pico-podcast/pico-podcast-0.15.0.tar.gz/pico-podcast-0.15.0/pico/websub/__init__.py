from django.db import transaction
from . import signals


@transaction.atomic
def subscribe(topic):
    from .models import Subscription

    obj = Subscription.objects.discover(topic)
    transaction.on_commit(obj.subscribe)

    return obj


def unsubscribe(topic):
    from .models import Subscription

    subscriptions = Subscription.objects.filter(topic=topic)
    for obj in subscriptions:
        obj.unsubscribe()

    return subscriptions


__all__ = (
    'subscribe',
    'unsubscribe',
    'signals'
)
