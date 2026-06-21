from urllib.parse import urlparse

MAX_LINK_URL_LEN = 2048


def valid_link_url(value):
    if not value:
        return True
    parsed = urlparse(str(value))
    return len(str(value)) <= MAX_LINK_URL_LEN and parsed.scheme in ('http', 'https') and bool(parsed.netloc)
