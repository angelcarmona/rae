'''
Cliente para el diccionario de la RAE (https://www.rae.es)

Proporciona funciones para consultar entradas del diccionario de la
Real Academia Española
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
    Devuelve la palabra del día en https://www.rae.es

    Returns:
        list[dict] | None: Entrada del diccionario para la palabra del día o
        None si la petición falla.
    '''
    try:
        soup = _fetch_soup(BASE_URL)
        word = soup.find('span', class_='c-word-day__word').get_text(strip=True)
        return search_by_word(word)
    except requests.exceptions.RequestException:
        return None


def search_by_word(word):
    '''
    Busca una palabra en el diccionario de la RAE.

    Args:
        word (str): Palabra a buscar.

    Returns:
        list[dict] | None: Lista de artículos con título, introducción y
        definiciones o None si la petición falla.
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
    Obtiene una palabra aleatoria de la RAE.

    Returns:
        list[dict] | None: Entrada del diccionario para una palabra aleatoria o
        None si la petición falla.
    '''
    try:
        soup = _fetch_soup(f'{BASE_URL}/?m=random')
        return _parse_articles(soup)
    except requests.exceptions.RequestException:
        return None


def words_starting_with(prefix):
    '''
    Devuelve todas las palabras del diccionario de la RAE que empiezan por el
    prefijo proporcionado.

    Args:
        prefix (str): Prefijo a buscar.

    Returns:
        list[str] | None: Lista de palabras que empiezan por el prefijo o None
        si la petición falla.
    '''
    try:
        return _get_words(f'{BASE_URL}/{prefix}?m=31')
    except requests.exceptions.RequestException:
        return None


def words_ending_with(suffix):
    '''
    Devuelve todas las palabras del diccionario de la RAE que terminan con el
    sufijo proporcionado.

    Args:
        suffix (str): Sufijo a buscar.

    Returns:
        list[str] | None: Lista de palabras que terminan con el sufijo o None si
        la petición falla.
    '''
    try:
        return _get_words(f'{BASE_URL}/{suffix}?m=32')
    except requests.exceptions.RequestException:
        return None


def contains(substring):
    '''
    Devuelve todas las palabras del diccionario de la RAE que contienen la
    subcadena proporcionada.

    Args:
        substring (str): Subcadena a buscar.

    Returns:
        list[str] | None: Lista de palabras que contienen la subcadena o None si
        la petición falla.
    '''
    try:
        return _get_words(f'{BASE_URL}/{substring}?m=33')
    except requests.exceptions.RequestException:
        return None


def anagrams(word):
    '''
    Devuelve todos los anagramas de la palabra dada presentes en el diccionario
    de la RAE.

    Args:
        word (str): Palabra para la que buscar anagramas.

    Returns:
        list[str] | None: Lista de anagramas encontrados en el diccionario o
        None si la petición falla.
    '''
    try:
        return _get_words(f'{BASE_URL}/{word}?m=anagram')
    except requests.exceptions.RequestException:
        return None


def abbreviations_and_symbols():
    '''
    Obtiene abreviaturas y símbolos de la RAE.

    Returns:
        dict | None: Diccionario con notas, abreviaturas y símbolos o None si la
        petición falla.
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
