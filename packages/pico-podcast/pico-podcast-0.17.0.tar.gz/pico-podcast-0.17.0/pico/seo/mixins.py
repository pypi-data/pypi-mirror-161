from django.contrib.staticfiles.storage import staticfiles_storage
from pico.conf import settings
from django.core.files import File
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.http import urlquote
import json
import os


class SEOMixin(object):
    seo_title = ''
    seo_description = ''
    robots = ''
    valid_canonical_querystring_params = ()

    def get_seo_title(self):
        return self.seo_title

    def get_seo_description(self):
        return self.seo_description

    def get_valid_canonical_querystring_params(self):
        params = list(self.valid_canonical_querystring_params)

        if hasattr(self, 'paginate_by'):
            page = self.request.GET.get('page', '1')
            if page != '1':
                params.append('page')

        return params

    def get_canonical_url(self):
        if hasattr(self, 'canonical_url'):
            url = self.request.build_absolute_uri(
                reverse(self.canonical_url)
            ) + '?'
        else:
            url = self.request.build_absolute_uri('.') + '?'

        params = self.get_valid_canonical_querystring_params()
        for key in sorted(self.request.GET.keys()):
            if key not in params:
                continue

            for value in self.request.GET.getlist(key):
                url += '%s=%s&' % (
                    urlquote(key),
                    urlquote(value)
                )

        return url[:-1]

    def get_robots(self):
        return self.robots

    def get_context_data(self, **kwargs):
        return {
            'seo_title': self.get_seo_title(),
            'seo_description': self.get_seo_description(),
            'robots_content': self.get_robots(),
            'canonical_url': self.get_canonical_url(),
            **super().get_context_data(**kwargs)
        }

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        robots = self.get_robots()

        if robots:
            response['X-Robots-Tag'] = robots

        return response


class OpenGraphMixin(object):
    og_locale = 'en-GB'
    og_type = 'article'
    og_title = settings.NETWORK_NAME
    og_description = ''
    og_site_name = settings.NETWORK_NAME

    twitter_card = 'summary_large_image'
    twitter_title = ''
    twitter_description = ''

    def get_og_locale(self):
        return self.og_locale

    def get_og_type(self):
        return self.og_type

    def get_og_title(self):
        return self.og_title

    def get_og_description(self):
        return self.og_description

    def get_og_image(self):
        if hasattr(self, 'og_image'):
            return staticfiles_storage.url(self.og_image)

    def get_og_url(self):
        return self.request.build_absolute_uri(self.request.path)

    def get_og_site_name(self):
        return self.og_site_name

    def get_og_tags(self):
        tags = [
            {
                'property': 'locale',
                'content': self.get_og_locale()
            },
            {
                'property': 'type',
                'content': self.get_og_type()
            },
            {
                'property': 'title',
                'content': self.get_og_title()
            },
            {
                'property': 'description',
                'content': self.get_og_description()
            },
            {
                'property': 'url',
                'content': self.get_og_url()
            },
            {
                'property': 'site',
                'content': self.get_og_site_name()
            }
        ]

        image = self.get_og_image()
        if isinstance(image, File) and image:
            tags.extend(
                [
                    {
                        'property': 'image',
                        'content': image.url
                    }
                ]
            )
        elif isinstance(image, str) and image:
            tags.append(
                {
                    'property': 'image',
                    'content': image
                }
            )

        return tags

    def get_twitter_card(self):
        return self.twitter_card

    def get_twitter_title(self):
        return self.twitter_title or self.get_og_title()

    def get_twitter_description(self):
        return self.twitter_description or self.get_og_description()

    def get_twitter_site(self):
        if settings.TWITTER_SITE:
            return '@%s' % settings.TWITTER_SITE

    def get_twitter_creator(self):
        if settings.TWITTER_USERNAME:
            return '@%s' % settings.TWITTER_USERNAME

    def get_twitter_tags(self):
        tags = [
            {
                'name': 'card',
                'content': self.get_twitter_card()
            },
            {
                'name': 'title',
                'content': self.get_twitter_title()
            },
            {
                'name': 'description',
                'content': self.get_twitter_description()
            },
            {
                'name': 'site',
                'content': self.get_twitter_site()
            },
            {
                'name': 'creator',
                'content': self.get_twitter_creator()
            }
        ]

        image = self.get_og_image()
        if isinstance(image, File) and image:
            tags.append(
                {
                    'name': 'image',
                    'content': image.url
                }
            )
        elif isinstance(image, str) and image:
            tags.append(
                {
                    'name': 'image',
                    'content': image
                }
            )

        return tags

    def get_context_data(self, **kwargs):
        return {
            'og_tags': self.get_og_tags(),
            'twitter_tags': self.get_twitter_tags(),
            **super().get_context_data(**kwargs)
        }


class OpenGraphArticleMixin(OpenGraphMixin):
    og_type = 'article'
    article_publisher = 'https://www.facebook.com/podiant'
    article_author = ''
    article_section = ''
    article_published_time = ''

    def get_article_publisher(self):
        return self.article_publisher

    def get_article_author(self):
        return self.article_author

    def get_article_section(self):
        return self.article_section

    def get_article_published_time(self):
        return self.article_published_time

    def get_article_tags(self):
        return [
            {
                'property': 'publisher',
                'content': self.get_article_publisher()
            },
            {
                'property': 'author',
                'content': self.get_article_author()
            },
            {
                'property': 'section',
                'content': self.get_article_section()
            },
            {
                'property': 'published_time',
                'content': self.get_article_published_time()
            }
        ]

    def get_context_data(self, **kwargs):
        return {
            'article_tags': self.get_article_tags(),
            **super().get_context_data(**kwargs)
        }


class LinkedDataMixin(object):
    ld_type = 'Thing'

    def get_ld_type(self):
        return self.ld_type

    def __load_fixture(self, name):
        app, fixture = name.split('.')
        filename = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            app,
            'fixtures',
            'ld',
            '%s.json' % fixture
        )

        return self.__prepare_fixture(filename)

    def __prepare_fixture(self, filename):
        with open(filename, 'rb') as f:
            data = json.load(f)

        for key, value in data.items():
            if isinstance(value, dict):
                import_name = value.pop('@import', None)
                if import_name:
                    import_fixture = self.__load_fixture(import_name)
                    data[key] = {
                        **import_fixture,
                        **value
                    }

        return data

    def get_ld_attributes(self):
        if hasattr(self, 'ld_attributes'):
            return self.ld_attributes

        if hasattr(self, 'ld_fixture'):
            return self.__load_fixture(self.ld_fixture)

        return {}

    def get_ld_url(self):
        if hasattr(self, 'ld_url'):
            return self.request.build_absolute_uri(
                reverse(self.ld_url)
            )

    def get_linked_data(self):
        data = {
            '@context': 'https://schema.org',
            '@type': self.get_ld_type(),
            **self.get_ld_attributes()
        }

        url = self.get_ld_url()
        if 'url' not in data and url:
            data['url'] = url

        return data

    def get_context_data(self, **kwargs):
        local = {}

        def get_json_ld():
            if 'ld' not in local:
                local['ld'] = mark_safe(
                    json.dumps(
                        kwargs.get('json_ld', self.get_linked_data()),
                        indent=4
                    )
                )

            return local['ld']

        return {
            'json_ld': get_json_ld,
            **super().get_context_data(**kwargs)
        }
