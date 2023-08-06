from django.core.exceptions import ImproperlyConfigured
from django.http.response import HttpResponsePermanentRedirect, Http404
from pico.conf import settings
from urllib.parse import urlsplit, urlunsplit
from django.urls import resolve
from .models import Podcast, Page
from .views import PageDetailView, PostListView, PostDetailView


def podcast_domain_middleware(get_response):
    def domains_middleware(request):
        scheme, domain, path, querystring, fragment = urlsplit(
            request.build_absolute_uri()
        )

        if domain.startswith('www.'):
            return HttpResponsePermanentRedirect(
                urlunsplit(
                    (
                        scheme,
                        domain[4:],
                        path,
                        querystring,
                        fragment
                    )
                )
            )

        for podcast in Podcast.objects.filter(
            domain=domain
        ):
            request.urlconf = 'pico.podcasts.urls'
            request.podcast = podcast

        return get_response(request)

    def slugs_middleware(request):
        resolved = resolve(request.path)
        if resolved is not None:
            kwargs = resolved.kwargs

            if 'podcast' in kwargs:
                for podcast in Podcast.objects.filter(
                    slug=kwargs['podcast']
                ):
                    request.podcast = podcast
                    return get_response(request)

                if kwargs['podcast'] == 'blog':
                    request.podcast = None

                    if 'slug' in kwargs:
                        view = PostDetailView.as_view()
                        response = view(request, slug=kwargs['slug'])
                    else:
                        view = PostListView.as_view()
                        response = view(request)

                    return response.render()

                for page in Page.objects.filter(
                    slug=kwargs['podcast'],
                    podcast=None
                ):
                    view = PageDetailView.as_view()
                    request.podcast = None
                    response = view(request, slug=page.slug)
                    return response.render()

                raise Http404('Podcast not found.')

        return get_response(request)

    if settings.DOMAINS_OR_SLUGS == 'domains':
        return domains_middleware

    if settings.DOMAINS_OR_SLUGS == 'slugs':
        return slugs_middleware

    raise ImproperlyConfigured(
        'domains_or_slugs must be set to \'domains\' or \'slugs\'.'
    )
