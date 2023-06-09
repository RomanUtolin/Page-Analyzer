from page_analyzer import app
import requests
from bs4 import BeautifulSoup


def get_seo_data(url):
    tags = ['meta', 'h1', 'title']
    dict_tags = {'description': '',
                 'h1': '',
                 'title': '',
                 'status_code': ''}
    try:
        response = requests.get(url)
        response.raise_for_status()
        dict_tags['status_code'] = response.status_code
        app.app.logger.info(f'Successfully response for {url}')
        return find_tag(response, tags, dict_tags)
    except requests.exceptions.RequestException as error:
        app.app.logger.warning(error)


def find_tag(response, tags, dict_tags):
    soup = BeautifulSoup(response.text, 'html.parser')
    for t in tags:
        if t == 'meta':
            find = soup.find('meta', attrs={"name": "description"})
            if find:
                dict_tags['description'] = find.get("content")
        else:
            if soup.find(t):
                dict_tags[t] = soup.find(t).getText()
    return dict_tags
