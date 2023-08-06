from dateutil.parser import parse as parse_date
from django.db import transaction
from django.db.models import QuerySet
from django.utils import html, text, timezone
from feedparser import parse as parse_feed
from html2text import html2text
from urllib.parse import urlparse
from .utils import download, compare_image


RANDOM_IMAGE_URL = 'https://source.unsplash.com/random'


class PodcastQuerySet(QuerySet):
    def ingest(self, url, feed=None, episode_callback=None):
        if feed is None:
            feed = parse_feed(url)

        meta, episodes = feed['feed'], feed['items']
        image = meta.get('image', {}).get('href', '')
        slug = text.slugify(meta['title'])
        domain = ''

        for link in meta.get('links', []):
            if link.get('rel') == 'self':
                slug = urlparse(link['href']).path.split('/')[-1]
            elif link.get('rel') == 'alternate':
                domain = urlparse(link['href']).netloc

        while domain.startswith('www.'):
            domain = domain[4:]

        podcast = self.create(
            name=meta['title'],
            slug=slug,
            domain=domain,
            rss_feed_url=url,
            artwork=image and download(image) or None,
            description=html2text(meta['description'], bodywidth=0)
        )

        for episode in episodes:
            with transaction.atomic():
                podcast.episodes.ingest(
                    podcast,
                    episode,
                    callback=episode_callback
                )

        return podcast


class EpisodeQuerySet(QuerySet):
    def ingest(self, podcast, item, callback=None):
        from .models import Host

        season_number = item.get('itunes_season')
        episode_number = item.get('itunes_episode')
        episode_type = item.get('itunes_episodetype')
        author = item.get('author')
        season = None

        if season_number:
            season = podcast.seasons.filter(
                number=season_number
            ).first()

            if season is None:
                season = podcast.seasons.create(
                    number=season_number
                )

        image = item.get('image', {}).get('href', '')
        if image:
            image = download(image)
            if not compare_image(image, podcast.artwork):
                image = None

        description = item.get('summary')
        summary = html.strip_tags(item.get('subtitle'))

        for detail in item.get('content', []):
            if detail['type'] == 'text/html':
                description = detail['value']
                break

        enclosure = None
        for link in item.get('links', []):
            if link['rel'] == 'enclosure':
                enclosure = link['href']

        date = parse_date(item['published'])
        episode = podcast.episodes.create(
            guid=item['id'],
            title=item['title'],
            published=date,
            season=season,
            number=episode_number or 0,
            bonus=episode_type == 'bonus',
            trailer=episode_type == 'trailer',
            artwork=image,
            summary=summary,
            enclosure_url=enclosure,
            feed_description=html2text(description, bodywidth=0)
        )

        if author:
            for name in author.split(','):
                name_stripped = name.strip()
                host = Host.objects.filter(
                    name__iexact=name_stripped
                ).first()

                if host is None:
                    host = Host.objects.create(
                        name=name_stripped,
                        slug=text.slugify(name_stripped),
                        photo=download(RANDOM_IMAGE_URL)
                    )

                episode.hosts.add(host)
                podcast.hosts.add(host)

        if callable(callback):
            callback(episode)

        return episode


class PostQuerySet(QuerySet):
    def published(self):
        return self.filter(
            published__lte=timezone.now()
        )
