from django.template.loader import render_to_string
from pico import miditags


@miditags.register('embed')
class EmbedHandler(miditags.HandlerBase):
    def handle(self, url):
        return render_to_string(
            'podcasts/embed_iframe.html',
            {
                'url': url,
                'height': 600
            }
        )
