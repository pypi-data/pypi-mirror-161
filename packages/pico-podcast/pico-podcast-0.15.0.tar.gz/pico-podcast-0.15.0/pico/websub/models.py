from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from hashlib import sha1
from uuid import uuid4
from .exceptions import SubscriptionError, SignatureValidationError
from .query import SubscriptionQuerySet
from .signals import published
import hmac
import random
import requests
import string


class Subscription(models.Model):
    objects = SubscriptionQuerySet.as_manager()
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    hub = models.URLField(max_length=512)
    topic = models.URLField(max_length=512)
    lease_seconds = models.PositiveIntegerField(null=True)
    secret = models.CharField(max_length=64)
    confirmed = models.DateTimeField(null=True, editable=False)
    expires = models.DateTimeField(null=True, editable=False)

    def __str__(self):
        return self.topic

    def save(self, *args, **kwargs):
        if not self.secret:
            self.secret = ''.join(
                random.sample(string.printable, 64)
            )

        super().save(*args, **kwargs)

    def get_callback_url(self):
        return 'http%s://%s%s' % (
            settings.WEBSUB_CALLBACK_SECURE and 's' or '',
            settings.WEBSUB_CALLBACK_DOMAIN,
            reverse('websub_callback', args=(self.pk,))
        )

    def __command(self, mode):
        params = {
            'hub.callback': self.get_callback_url(),
            'hub.mode': mode,
            'hub.topic': self.topic
        }

        if self.lease_seconds is not None:
            params['hub.lease_seconds'] = self.lease_seconds

        if self.secret:
            params['hub.secret'] = self.secret

        response = requests.post(self.hub, data=params)
        if response.status_code >= 200 and response.status_code < 400:
            return True

        if response.status_code >= 500:
            raise Exception('The hub encountered an error')

        if 'application/json' in response.headers['Content-Type']:
            json = response.json()
            error = json.get('error')

            if error:
                error_description = json.get('error_description')

                if error_description:
                    raise SubscriptionError(error, error_description)

                raise SubscriptionError(error)

        raise SubscriptionError(response.reason)

    def subscribe(self):
        return self.__command('subscribe')

    def unsubscribe(self):
        return self.__command('unsubscribe')

    def lease(self, seconds):
        delta = timezone.timedelta(seconds=int(seconds))
        self.expires = timezone.now() + delta

    def validate_signature(self, request):
        if self.secret:
            supplied = request.META.get('HTTP_X_HUB_SIGNATURE')
            computed = 'sha1=%s' % (
                hmac.new(
                    self.secret.encode('utf-8'),
                    request.body,
                    sha1
                ).hexdigest()
            )

            if supplied != computed:
                raise SignatureValidationError('Signature is invalid.')

    def confirm_subscribe(self, commit=True):
        self.confirmed = timezone.now()

        if commit:
            self.save()

    def confirm_unsubscribe(self, commit=True):
        if commit:
            self.delete()

    def receive(self, data):
        published.send(
            type(self),
            topic=self.topic,
            data=data
        )

    class Meta:
        unique_together = ('topic', 'hub')
