import requests


def get_status_code(url):
    for u in url:
        code = requests.get(u).status_code
        return code
