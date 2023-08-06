from bs4 import BeautifulSoup
from django.db.models import QuerySet
from urllib.parse import urljoin
from .exceptions import DiscoveryError
import feedparser
import requests


class SubscriptionQuerySet(QuerySet):
    def discover(self, topic):
        response = requests.head(topic, allow_redirects=True)
        rel_topic = topic

        if response.status_code == 200:
            hub = response.links.get('hub')
            rel_self = response.links.get('self')

            if rel_self:
                rel_topic = rel_self['url']

            if hub is not None:
                obj, created = self.get_or_create(
                    hub=urljoin(topic, hub['url']),
                    topic=urljoin(topic, rel_topic)
                )

                return obj

        content_type = response.headers['Content-Type']

        if 'text/html' in content_type:
            response = requests.get(topic)
            soup = BeautifulSoup(response.content, 'html.parser')
            head = soup.find('head')

            if head is not None:
                for link in head.find_all('link'):
                    rel = link.get('rel')
                    if 'self' in rel:
                        rel_topic = link.get('href')
                        break

                for link in head.find_all('link'):
                    rel = link.get('rel')
                    if 'hub' in rel:
                        obj, created = self.get_or_create(
                            hub=urljoin(topic, link.get('href')),
                            topic=urljoin(topic, rel_topic)
                        )

                        return obj

        if (
            'text/xml' in content_type or
            'application/atom+xml' in content_type or
            'application/rss+xml' in content_type or
            'application/xml' in content_type
        ):
            response = requests.get(topic)
            feed = feedparser.parse(response.content)

            for link in feed.feed.links:
                if link.rel == 'self':
                    rel_topic = link.href
                    break

            for link in feed.feed.links:
                if link.rel == 'hub':
                    obj, created = self.get_or_create(
                        hub=urljoin(topic, link.get('href')),
                        topic=urljoin(topic, rel_topic)
                    )

                    return obj

        raise DiscoveryError('Unable to discover WebSub hub URL.')
