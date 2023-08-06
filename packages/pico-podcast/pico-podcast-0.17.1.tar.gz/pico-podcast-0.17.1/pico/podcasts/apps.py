from django.apps import AppConfig
from watson import search as watson
from .search import EpisodeSearchAdapter, PostSearchAdapter, PageSearchAdapter


class PodcastsConfig(AppConfig):
    name = 'pico.podcasts'

    def ready(self):
        Episode = self.get_model('Episode')
        Post = self.get_model('Post')
        Page = self.get_model('Page')

        watson.register(
            Episode.objects.all(),
            EpisodeSearchAdapter
        )

        watson.register(
            Post.objects.published(),
            PostSearchAdapter
        )

        watson.register(
            Page.objects.all(),
            PageSearchAdapter
        )
