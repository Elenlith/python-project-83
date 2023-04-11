import validators
from urllib.parse import urlparse


def normalize_url(raw_url):
    url = urlparse(raw_url)
    return f"{url.scheme}://{url.netloc}"


def validate_url(raw_url):
    """
    Check URL if it's correct (using validators.url),
    not empty and not more than 255 characters
    :param raw_url: URL
    :return: List of alerts
    """
    alerts = []
    if not validators.url(raw_url) or len(raw_url) > 255:
        alerts.append('Некорректный URL')
        if not raw_url:
            alerts.append('URL обязателен')
        return alerts
