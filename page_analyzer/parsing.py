import requests
import bs4


def get_seo_data(url):
    for u in url:
        url = u
    try:
        get_html = requests.get(url)
        status_code = get_html.status_code
        return status_code
    except Exception:
        return False
