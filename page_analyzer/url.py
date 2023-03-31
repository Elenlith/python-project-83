from validators import url as valid
from urllib.parse import urlparse


def get_domain(url):
    url = urlparse(url)
    return f"{url.scheme}://{url.netloc}"


def validate(raw_url):
    """
    Check URL if it's correct (using validators.url),
    not empty and not more than 255 characters
    :param raw_url: URL
    :return: List of alerts
    """
    alerts = []
    url = get_domain(raw_url)
    if not raw_url:
        alerts.append('URL обязателен')
    if not valid(raw_url):
        alerts.append('Некорректный URL')
    if len(url) > 255:
        alerts.append('URL превышает 255 символов')
    return alerts
