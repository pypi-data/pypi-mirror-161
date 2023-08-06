from django.test import TestCase
from mock import patch
from .exceptions import SubscriptionError
from .models import Subscription
from . import mock_requests


class SubscriptionTests(TestCase):
    @patch('requests.head', mock_requests.head)
    def test_header_discover(self):
        obj = Subscription.objects.discover(
            topic='https://websub.rocks/blog/100/MuYa9M1wblw8OvdfESZJ'
        )

        self.assertEqual(
            obj.hub,
            'https://websub.rocks/blog/100/MuYa9M1wblw8OvdfESZJ/hub'
        )

    @patch('requests.head', mock_requests.head)
    @patch('requests.get', mock_requests.get)
    def test_html_discover(self):
        obj = Subscription.objects.discover(
            topic='https://websub.rocks/blog/101/rxeK2WU8FeV66gkYLwGj'
        )

        self.assertEqual(
            obj.hub,
            'https://websub.rocks/blog/101/rxeK2WU8FeV66gkYLwGj/hub'
        )

    @patch('requests.head', mock_requests.head)
    @patch('requests.get', mock_requests.get)
    def test_atom_discover(self):
        obj = Subscription.objects.discover(
            topic='https://websub.rocks/blog/102/eha8Uik68G9Tb5L5rtbH'
        )

        self.assertEqual(
            obj.hub,
            'https://websub.rocks/blog/102/eha8Uik68G9Tb5L5rtbH/hub'
        )

    @patch('requests.head', mock_requests.head)
    @patch('requests.get', mock_requests.get)
    def test_rss_discover(self):
        obj = Subscription.objects.discover(
            topic='https://websub.rocks/blog/103/eHjHmBxAu0XmwkTqoDmi'
        )

        self.assertEqual(
            obj.hub,
            'https://websub.rocks/blog/103/eHjHmBxAu0XmwkTqoDmi/hub'
        )

    @patch('requests.post', mock_requests.post)
    def test_different_self_discover(self):
        obj = Subscription.objects.discover(
            'https://websub.rocks/blog/200/pfoAHC07WzZgG1rA1uHS'
        )

        self.assertEqual(
            obj.topic,
            'https://websub.rocks/blog/200/pfoAHC07WzZgG1rA1uHS?self=other'
        )

    @patch('requests.post', mock_requests.post)
    def test_subscribe_verification_failed(self):
        obj = Subscription.objects.create(
            hub='https://websub.rocks/blog/100/MuYa9M1wblw8OvdfESZJ/hub',
            topic='https://websub.rocks/blog/100/MuYa9M1wblw8OvdfESZJ'
        )

        with self.assertRaises(SubscriptionError) as ctx:
            obj.subscribe()

        self.assertEqual(ctx.exception.args[0], 'verification_failed')

    @patch('requests.post', mock_requests.post)
    def test_subscribe_success(self):
        obj = Subscription.objects.create(
            hub='https://pubsubhubbub.appspot.com/',
            topic='https://feeds.transistor.fm/podcode',
            lease_seconds=86400
        )

        response = obj.subscribe()
        self.assertTrue(response)
