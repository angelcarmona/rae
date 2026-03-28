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

            if item:
                definitions.append(_clean_text(item))

        articles.append({
            'title': title,
            'intro': intro,
            'definitions': definitions
        })

    return articles


def _find_next_words_page(soup):
    for a in soup.select('nav.c-pagination a.c-pagination__link[href]'):
        if a.get_text(strip=True) == 'Siguiente':
            return BASE_URL + a['href']
    return None


def _get_words(url):
    words = []
    visited = set()

    while url and url not in visited:
        visited.add(url)
        soup = _fetch_soup(url)

        for a in soup.select('div.u-grid.u-gap-y-3 article h3'):
            word = a.get('data-eti') or a.get_text(strip=True)
            words.append(word)

        url = _find_next_words_page(soup)

    return words


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


def words_starting_with(prefix):
    '''
    Return all words from the RAE dictionary that start with the given prefix.

    Args:
        prefix (str): Prefix to search.

    Returns:
        list[str] | None: List of words that start with the prefix,
        or None if request fails.
    '''
    try:
        return _get_words(f'{BASE_URL}/{prefix}?m=31')
    except requests.exceptions.RequestException:
        return None


def words_ending_with(suffix):
    '''
    Return all words from the RAE dictionary that end with the given suffix.

    Args:
        suffix (str): Suffix to search.

    Returns:
        list[str] | None: List of words that end with the suffix,
        or None if request fails.
    '''
    try:
        return _get_words(f'{BASE_URL}/{suffix}?m=32')
    except requests.exceptions.RequestException:
        return None


def contains(substring):
    '''
    Return all words from the RAE dictionary that contain the given substring.

    Args:
        substring (str): Substring to search.

    Returns:
        list[str] | None: List of words that contain the substring,
        or None if request fails.
    '''
    try:
        return _get_words(f'{BASE_URL}/{substring}?m=33')
    except requests.exceptions.RequestException:
        return None


def anagrams(word):
    '''
    Return all anagrams of the given word present in the RAE dictionary.

    Args:
        word (str): Word to search anagrams for.

    Returns:
        list[str] | None: List of anagrams found in the dictionary,
        or None if request fails.
    '''
    try:
        return _get_words(f'{BASE_URL}/{word}?m=anagram')
    except requests.exceptions.RequestException:
        return None


def abbreviations_and_symbols():
    '''
    Retrieve abbreviations and symbols metadata from RAE.

    Returns:
        dict | None: Dictionary with notes, abbreviations and symbols,
        or None if request fails.
    '''
    try:
        soup = _fetch_soup(f'{BASE_URL}/contenido/abreviaturas-y-signos-empleados')

        data = {
            'notes': [],
            'abbreviations': [],
            'symbols': []
        }

        ul = soup.find('div', id='content').find('ul')
        data['notes'] = [
            _clean_text(li)
            for li in ul.find_all('li', recursive=False)
        ]

        table = soup.find('div', id='abbreviation').find('table')
        for row in table.find_all('tr'):
            cells = row.find_all('td')
            key = _clean_text(cells[0])
            value = _clean_text(cells[1])
            data['abbreviations'].append((key, value))

        symbol_div = soup.find('div', id='symbol')
        table = symbol_div.find('table')
        for row in table.find_all('tr'):
            cells = row.find_all('td')
            key = _clean_text(cells[0])
            value = _clean_text(cells[1])
            data['symbols'].append((key, value))

        return data
    except requests.exceptions.RequestException:
        return None
