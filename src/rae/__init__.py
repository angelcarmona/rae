'''
RAE dictionary client

Provides utilities to fetch and parse entries from the
Real Academia Española dictionary
'''

import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://dle.rae.es'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}


def _clean_text(node):
    return ' '.join(node.stripped_strings)


def _fetch_soup(url):
    r = requests.get(url, headers=HEADERS, timeout=5)
    r.raise_for_status()
    return BeautifulSoup(r.text, 'lxml')


def _parse_articles(soup):
    articles = []

    for article in soup.select('article.o-main__article'):
        title_node = article.select_one('h1.c-page-header__title')
        intro_node = article.select_one('div.c-text-intro')

        title = _clean_text(title_node) if title_node else None
        intro = _clean_text(intro_node) if intro_node else None

        definitions = []
        for li in article.select('li.j'):
            item = li.select_one('div.c-definitions__item')
            if not item:
                continue
            definitions.append(_clean_text(item))

        articles.append({
            'title': title,
            'intro': intro,
            'definitions': definitions
        })

    return articles


def word_of_the_day():
    '''
    Retrieve today's word from RAE and return its parsed entries.

    Returns:
        list[dict] | None: Parsed dictionary entries for the word of the day,
        or None if request fails.
    '''
    try:
        soup = _fetch_soup(BASE_URL)
        word = soup.find('span', class_='c-word-day__word').get_text(strip=True)
        return search_by_word(word)
    except requests.exceptions.RequestException:
        return None


def search_by_word(word):
    '''
    Search a word in the RAE dictionary.

    Args:
        word (str): Word to search.

    Returns:
        list[dict] | None: List of articles with title, intro and definitions,
        or None if request fails.
    '''
    try:
        soup = _fetch_soup(f'{BASE_URL}/{word}')
        return _parse_articles(soup)
    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.HTTPError:
        return None
    except requests.exceptions.RequestException:
        return None


def random_word():
    '''
    Retrieve a random word from RAE and return its parsed entries.

    Returns:
        list[dict] | None: Parsed dictionary entries for a random word,
        or None if request fails.
    '''
    try:
        soup = _fetch_soup(f'{BASE_URL}/?m=random')
        return _parse_articles(soup)
    except requests.exceptions.RequestException:
        return None

