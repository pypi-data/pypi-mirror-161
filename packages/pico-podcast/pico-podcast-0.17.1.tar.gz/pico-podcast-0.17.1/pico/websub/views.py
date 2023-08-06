from django.db import transaction
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from requests.utils import parse_header_links
from .exceptions import SignatureValidationError
from .models import Subscription
import logging


@method_decorator(csrf_exempt, name='dispatch')
class SubscriptionCallbackView(View):
    content_type = 'text/plain'

    @transaction.atomic
    def get(self, request, pk):
        try:
            obj = Subscription.objects.select_for_update().get(
                pk=pk
            )
        except Subscription.DoesNotExist:
            return HttpResponse(
                'Subscription not found.',
                status=410,
                content_type=self.content_type
            )

        try:
            mode = request.GET.get('hub.mode')
            topic = request.GET.get('hub.topic')

            if topic != obj.topic:
                return HttpResponse(
                    'Topic does not match.',
                    status=404,
                    content_type=self.content_type
                )

            challenge = request.GET.get('hub.challenge')
            lease_seconds = request.GET.get('hub.lease_seconds')
            method = getattr(obj, 'confirm_%s' % mode, None)

            if method is None or not callable(method):
                return HttpResponse(
                    'Invalid mode. Expected \'subscribe\' or \'unsubscribe\'.',
                    status=400,
                    content_type=self.content_type
                )

            if lease_seconds is not None:
                try:
                    obj.lease(lease_seconds)
                except ValueError:
                    return HttpResponse(
                        '\'hub.lease_seconds\' must be an integer.',
                        status=400,
                        content_type=self.content_type
                    )

            if self.request.method == 'GET':
                method()

            return HttpResponse(
                challenge,
                content_type=self.content_type
            )
        except Exception as ex:  # pragma: no cover
            logging.error(
                'Error confirming %s request', mode,
                exc_info=True,
                extra={
                    'mode': mode,
                    'topic': topic,
                    'challenge': challenge,
                    'lease_seconds': lease_seconds
                }
            )

            return HttpResponse(
                str(ex.args[0]),
                status=500,
                content_type=self.content_type
            )

    def post(self, request, pk):
        try:
            obj = Subscription.objects.get(
                pk=pk,
                confirmed__isnull=False
            )
        except Subscription.DoesNotExist:
            return HttpResponse(
                'Subscription not found.',
                status=410,
                content_type=self.content_type
            )

        if obj.secret:
            try:
                obj.validate_signature(request)
            except SignatureValidationError as ex:
                return HttpResponse(
                    ex.args[0],
                    status=400,
                    content_type=self.content_type
                )

        links = request.META.get('HTTP_LINK')
        topic = None

        for link in parse_header_links(links):
            if link.get('rel') == 'self':
                topic = link['url']
                break

        if topic != obj.topic:
            return HttpResponse(
                'Topic does not match.',
                status=404,
                content_type=self.content_type
            )

        obj.receive(request.body)
        return HttpResponse(content_type=self.content_type)
