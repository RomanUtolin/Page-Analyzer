from urllib.parse import urlparse
import validators


def normalized_url(url):
    url = urlparse(url)
    normal_url = f'{url.scheme}://{url.netloc}'
    return normal_url


def validate_url(url):
    errors = []
    if len(url) == 0:
        errors.append(('URL обязателен', 'danger'))
    elif len(url) > 255:
        errors.append(('URL превышает 255 символов', 'danger'))
    elif not validators.url(url):
        errors.append(('Некорректный URL', 'danger'))
    return errors
