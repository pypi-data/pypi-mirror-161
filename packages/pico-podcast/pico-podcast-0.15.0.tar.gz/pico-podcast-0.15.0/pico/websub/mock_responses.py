from base64 import b64decode
import os


def __method(method, client, path):
    while path.startswith('/'):
        path = path[1:]

    while path.endswith('/'):
        path = path[:-1]

    filename = os.path.join(
        os.path.dirname(__file__),
        'fixtures',
        'mock_requests',
        '%s_%s.txt' % (method, path.replace('/', '__'))
    )

    reading_headers = True
    reading_method = False
    reading_data = False
    headers = {}
    body = None

    with open(filename, 'r') as f:
        for line in f.read().splitlines():
            if reading_headers:
                if line:
                    header, value = line.split(': ', 1)
                    meta = 'HTTP_%s' % header.replace('-', '_').upper()
                    headers[meta] = value
                    continue

                reading_headers = False
                reading_method = True
                continue

            if reading_method:
                method, path = line.split(' ', 1)
                reading_method = False
                reading_data = True
                continue

            if reading_data:
                body = b64decode(line.encode('utf-8'))

    return client.generic(
        method,
        path,
        body,
        **headers
    )


def get(client, path):
    return __method('GET', client, path)


def post(client, path):
    return __method('POST', client, path)
