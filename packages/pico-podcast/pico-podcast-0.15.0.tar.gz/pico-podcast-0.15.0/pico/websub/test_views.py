from datetime import datetime
from django.test import TestCase
from django.utils.timezone import utc
from mock import patch
from .models import Subscription
from . import mock_responses


def now():
    return datetime(2022, 1, 1, 0, 0, 0, 0, tzinfo=utc)


class SubscriptionCallbackViewTests(TestCase):
    def test_get_404(self):
        response = self.client.get(
            '/~/websub/6949ea36-a1a2-4b59-ad6f-cbf1ede40f21/'
        )

        self.assertEqual(response.status_code, 410)

    def test_get_wrong_topic(self):
        obj = Subscription.objects.create(
            hub='https://websub.rocks/blog/100/MuYa9M1wblw8OvdfESZJ/hub',
            topic='https://websub.rocks/blog/100/MuYa9M1wblw8OvdfESZJ'
        )

        response = self.client.get(
            '/~/websub/%s/' % obj.pk,
            {
                'topic': 'wrong'
            }
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.content.decode('utf-8'),
            'Topic does not match.'
        )

    def test_get_invalid_method(self):
        obj = Subscription.objects.create(
            hub='https://websub.rocks/blog/100/MuYa9M1wblw8OvdfESZJ/hub',
            topic='https://websub.rocks/blog/100/MuYa9M1wblw8OvdfESZJ'
        )

        response = self.client.get(
            '/~/websub/%s/' % obj.pk,
            {
                'hub.topic': obj.topic,
                'hub.mode': 'wrong'
            }
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content.decode('utf-8'),
            'Invalid mode. Expected \'subscribe\' or \'unsubscribe\'.'
        )

    def test_get_invalid_lease_seconds(self):
        obj = Subscription.objects.create(
            hub='https://websub.rocks/blog/100/MuYa9M1wblw8OvdfESZJ/hub',
            topic='https://websub.rocks/blog/100/MuYa9M1wblw8OvdfESZJ'
        )

        response = self.client.get(
            '/~/websub/%s/' % obj.pk,
            {
                'hub.topic': obj.topic,
                'hub.mode': 'subscribe',
                'hub.lease_seconds': 'wrong'
            }
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content.decode('utf-8'),
            '\'hub.lease_seconds\' must be an integer.'
        )

    @patch('django.utils.timezone.now', now)
    def test_get_confirmed(self):
        obj = Subscription.objects.create(
            hub='https://websub.rocks/blog/100/MuYa9M1wblw8OvdfESZJ/hub',
            topic='https://websub.rocks/blog/100/MuYa9M1wblw8OvdfESZJ'
        )

        response = self.client.get(
            '/~/websub/%s/' % obj.pk,
            {
                'hub.topic': obj.topic,
                'hub.mode': 'subscribe',
                'hub.lease_seconds': '3600',
                'hub.challenge': 'challenge'
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'challenge')

        obj = Subscription.objects.get(pk=obj.pk)
        self.assertEqual(
            obj.confirmed.isoformat(),
            '2022-01-01T00:00:00+00:00'
        )

    def test_post_invalid_signature(self):
        Subscription.objects.create(
            uuid='e110cdf5-1620-4d9c-9933-db2165c9f7e6',
            hub='https://pubsubhubbub.appspot.com/',
            topic='https://feeds.transistor.fm/podcode',
            secret='g J\rjv=R9M4Yi\x0c2,B\'bh?+XN.{q%A^>"#kFr$Q5&`nL~ImD}y8zClc@_sS6GZ|do',  # NOQA
            confirmed=now()
        )

        response = mock_responses.post(
            self.client,
            'websub/e110cdf5-1620-4d9c-9933-db2165c9f7e6/'
        )

        self.assertEqual(response.status_code, 400)

    def test_post_data(self):
        Subscription.objects.create(
            uuid='342a6fcf-b223-4869-b0ef-d60b21521356',
            hub='https://pubsubhubbub.appspot.com/',
            topic='https://feeds.transistor.fm/podcode',
            secret='P}yTdB!v)~Q7\t4zRnUh9ux^=%2&b0\n@DVer#W+[a<\rI>\\sAGj{`/8$El.fo\x0bp6wH',  # NOQA
            confirmed=now()
        )

        response = mock_responses.post(
            self.client,
            'websub/342a6fcf-b223-4869-b0ef-d60b21521356/'
        )

        self.assertEqual(response.status_code, 200)

    def test_unsubscribe(self):
        Subscription.objects.create(
            uuid='a16c77c8-86e7-4946-82f3-b452d56f1ed9',
            hub='https://pubsubhubbub.appspot.com/',
            topic='https://feeds.transistor.fm/leopard',
            confirmed=now()
        )

        mock_responses.get(
            self.client,
            'websub/a16c77c8-86e7-4946-82f3-b452d56f1ed9/'
        )
