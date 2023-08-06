from django_rq.decorators import job
from feedparser import parse


@job('default', timeout='15m')
def check_feed(podcast_id):
    from .models import Podcast

    podcast = Podcast.objects.get(pk=podcast_id)
    podcast.check_feed()


@job('default', timeout='15m')
def update_feed(podcast_id, feed_data):
    from .models import Podcast

    podcast = Podcast.objects.get(pk=podcast_id)
    podcast.update_feed(
        parse(feed_data)
    )
