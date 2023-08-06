from django.core.files import File
from mimetypes import guess_extension
from PIL import Image
from tempfile import mkstemp
from urllib.parse import urlparse
import imagehash
import os
import requests


def download(url):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    ext = os.path.splitext(urlparse(url).path)[-1]

    if not ext:
        ext = guess_extension(response.headers['Content-Type'])

    handle, filename = mkstemp(ext)

    try:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            os.write(handle, chunk)
    finally:
        os.close(handle)

    return File(
        open(filename, 'rb'),
    )


def compare_image(a, b):
    original_hash = imagehash.average_hash(Image.open(a))
    comparison_hash = imagehash.average_hash(Image.open(b))

    return (comparison_hash - original_hash)
