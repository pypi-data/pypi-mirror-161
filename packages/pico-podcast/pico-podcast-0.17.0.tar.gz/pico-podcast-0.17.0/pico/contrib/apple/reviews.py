from dateutil.parser import parse as parse_date
from django.utils.timezone import utc
from pyquery import PyQuery as pq
import logging
import re


ITUNES_STORE_URL_PATTERNS = (
    r'^https?:\/\/(?:.+\.)?itunes\.apple\.com\/.+\/podcast\/.+\/id(\d+)',
    r'^https?:\/\/itunes\.apple\.com\/(?:[\a-z]{2}\/)?podcast\/(?:[\w-])+\/id(\d+)',  # NOQA
    r'^https?:\/\/itunes\.apple\.com\/(?:[\a-z]{2}\/)?podcast\/id(\d+)',
    r'^https?:\/\/podcasts\.apple\.com\/.+\/podcast\/.+\/id(\d+)',
    r'^https?:\/\/pcr\.apple\.com\/id(\d+)'
)

CONCERN_PATTERN = re.compile(r'\?userReviewId=(\d+)')

ITUNES_STOREFRONTS = [
    {'name': 'Australia', 'id': '143460,12'},
    {'name': 'Canada', 'id': '143455-6,12'},
    {'name': 'Ireland', 'id': '143449,12'},
    {'name': 'New Zealand', 'id': '143461,12'},
    {'name': 'United Kingdom', 'id': '143444,12'},
    {'name': 'United States', 'id': '143441-1,12'}
]

WEBOBJECT_URL = (
    'http://itunes.apple.com/WebObjects/MZStore.woa/wa/customerReviews?'
    'displayable-kind=4&'
    'id=%s'
)

USER_AGENT = 'iTunes/10.3.1 (Macintosh; Intel Mac OS X 10.6.8) AppleWebKit/533.21.1'  # NOQA


def get_reviews(url):
    itunes_id = None
    for regex in ITUNES_STORE_URL_PATTERNS:
        matches = re.search(regex, url)
        if matches is None:  # pragma: no cover
            continue

        itunes_id = matches.groups()[0]
        break

    if itunes_id is None:  # pragma: no cover
        return

    for storefront in ITUNES_STOREFRONTS:
        try:
            dom = pq(
                WEBOBJECT_URL % itunes_id,
                headers={
                    'User-Agent': USER_AGENT,
                    'X-Apple-Store-Front': storefront['id'],
                    'X-Apple-Tz': '0',
                    'Accept-Language': 'en-us, en;q=0.50'
                }
            )
        except Exception:  # pragma: no cover
            logging.error(
                'Error parsing iTunes review response',
                exc_info=True
            )

        for r in [
            pq(rev)
            for rev in dom.find('.all-reviews .customer-review')
        ]:
            title = r.find('.customerReviewTitle').text()
            rating = r.find('.rating').attr('aria-label')
            meta = r.find('.user-info').text()
            reviewer = r.find('.user-info .reviewer').text()
            body = r.find('.content').text()
            concern = r.find('[report-a-concern-fragment-url]').attr(
                'report-a-concern-fragment-url'
            )

            if rating.endswith(' stars') or rating.endswith(' star'):
                rating = int(rating.split(' ')[0])

            meta = meta.strip().replace('\n', '').replace('\r', '')
            while '  ' in meta:  # pragma: no cover
                meta = meta.replace('  ', ' ')

            date = None
            if ' - ' in meta:
                for meta_part in meta.split(' - '):
                    try:
                        date = parse_date(meta_part).replace(tzinfo=utc)
                    except Exception:
                        continue
                    else:
                        break

            if date is None:  # pragma: no cover
                continue

            match = CONCERN_PATTERN.search(concern)
            yield dict(
                id=storefront['id'] + match.groups()[0],
                country=storefront['name'],
                title=title.strip(),
                body=body.strip(),
                author=reviewer.strip(),
                published=date,
                rating=rating
            )
