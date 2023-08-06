from .conf import settings as conf


def settings(request):
    return {
        'SITE_SETTINGS': conf
    }
