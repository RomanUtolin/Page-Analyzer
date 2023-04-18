from urllib.parse import urlparse
import validators


def normalized_url(url):
    url = urlparse(url)
    normal_url = f'{url.scheme}://{url.netloc}'
    return normal_url


def validate_url(url):
    errors = {}
    if not url:
        errors['text'] = 'URL обязателен'
    elif len(url) > 255:
        errors['text'] = 'URL превышает 255 символов'
    elif not validators.url(url):
        errors['text'] = 'Некорректный URL'
    return errors
