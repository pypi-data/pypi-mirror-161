import dj_database_url
import os


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = not not os.getenv('DEBUG')
ALLOWED_HOSTS = ['*']
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'markdownx',
    'easy_thumbnails',
    'django_rq',
    'watson',
    'captcha',
    'pico.podcasts',
    'pico.contact',
    'pico.seo',
    'pico.miditags',
    'pico.websub',
    'pico.theming'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'pico.podcasts.middleware.podcast_domain_middleware'
]

ROOT_URLCONF = 'pico.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(os.getcwd(), 'theme', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'pico.context_processors.settings'
            ]
        }
    }
]

WSGI_APPLICATION = 'pico.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///%s' % os.path.join(os.getcwd(), 'db.sqlite')
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'  # NOQA
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'  # NOQA
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'  # NOQA
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'  # NOQA
    }
]

LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'Europe/London'
USE_I18N = True
USE_L10N = True
USE_TZ = True
MEDIA_ROOT = os.getenv('MEDIA_ROOT', os.path.join(os.getcwd(), 'media'))
MEDIA_URL = os.getenv('MEDIA_URL', '/media/')
STATIC_URL = os.getenv('STATIC_URL', '/static/')
ASSETS_DIR = os.path.join(os.getcwd(), 'theme', 'assets')

if os.path.exists(ASSETS_DIR):
    STATICFILES_DIRS = [ASSETS_DIR]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MARKDOWN_STYLES = {
    'default': {
        'extensions': (
            'markdown.extensions.smarty',
            'python_markdown_nofollow',
            'fenced_code'
        )
    }
}

if not DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'  # NOQA
    STATIC_ROOT = os.getenv('STATIC_ROOT')

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
RQ_QUEUES = {
    'default': {
        'URL': REDIS_URL
    }
}

MARKDOWNX_MARKDOWN_EXTENSIONS = MARKDOWN_STYLES['default']['extensions']
MARKDOWNX_IMAGE_MAX_SIZE = {
    'size': (1204, 0),
    'quality': 90
}

WEBSUB_CALLBACK_SECURE = (
    os.getenv('WEBSUB_CALLBACK_SECURE') and
    True or
    not DEBUG
)

WEBSUB_CALLBACK_DOMAIN = (
    os.getenv('WEBSUB_CALLBACK_DOMAIN') or
    os.getenv('DOMAIN') or
    'localhost'
)

RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_PRIVATE_KEY')

REVIEW_DIRECTORIES = {
    'apple_podcasts': 'pico.contrib.apple.reviews.get_reviews'
}
