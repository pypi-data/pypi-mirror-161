from base64 import b64decode
from hashlib import md5
from requests import head as requests_head
from requests import get as requests_get
from requests import post as requests_post
from requests.utils import parse_header_links
import json
import os


class MockResponse(object):
    def __init__(self, fixture):
        with open(fixture, 'r') as f:
            data = f.read()

        reading_status = True
        reading_headers = False
        self.headers = {}
        body_encoded = ''

        for line in data.splitlines():
            if reading_status:
                status, reason = line.split(' ', 1)
                self.status_code = int(status)
                self.reason = reason

                reading_status = False
                reading_headers = True
                continue

            if not line and reading_headers:
                reading_headers = False
                continue

            if reading_headers and line:
                header, value = line.split(': ', 1)
                self.headers[header] = value
            elif line:
                body_encoded += line + '\n'

        self.content = b64decode(body_encoded)

    @property
    def links(self):
        header = self.headers.get('Link')
        linkdict = {}

        if header:
            links = parse_header_links(header)

            for link in links:
                key = link.get('rel') or link.get('url')
                linkdict[key] = link

        return linkdict

    def json(self):
        return json.loads(self.content)


def __method(method, mocked, url, *args, **kwargs):
    fixture = os.path.join(
        os.path.dirname(__file__),
        'fixtures',
        'mock_responses',
        '%s_%s.txt' % (
            method,
            md5(url.encode('utf-8')).hexdigest()
        )
    )

    return MockResponse(fixture)


def head(url, *args, **kwargs):
    return __method('HEAD', requests_head, url, *args, **kwargs)


def get(url, *args, **kwargs):
    return __method('GET', requests_get, url, *args, **kwargs)


def post(url, *args, **kwargs):
    return __method('POST', requests_post, url, *args, **kwargs)
