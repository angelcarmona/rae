import requests
from bs4 import BeautifulSoup

def clean_text(node):
    return ' '.join(node.stripped_strings)

def search_by_word(word):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }

    try:
        r = requests.get(f'https://dle.rae.es/{word}', headers=headers, timeout=5)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        articles = []

        for article in soup.select('article.o-main__article'):
            title_node = article.select_one('h1.c-page-header__title')
            intro_node = article.select_one('div.c-text-intro')

            title = clean_text(title_node) if title_node else None
            intro = clean_text(intro_node) if intro_node else None

            definitions = []
            for li in article.select('li.j'):
                item = li.select_one('div.c-definitions__item')
                if not item:
                    continue
                definitions.append(clean_text(item))

            articles.append({
                'title': title,
                'intro': intro,
                'definitions': definitions
            })

        return articles
    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.HTTPError:
        return None
    except requests.exceptions.RequestException:
        return None
