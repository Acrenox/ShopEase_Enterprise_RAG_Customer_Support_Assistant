import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup

RAW_DIR = Path('data/raw')
RAW_DIR.mkdir(parents=True, exist_ok=True)


def scrape_page(url: str) -> str:
    headers = {'User-Agent': 'ShopAssist-Demo/1.0'}
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    for tag in soup(['script', 'style', 'nav', 'footer']):
        tag.decompose()
    return soup.get_text(separator='\n')


def scrape_sources():
    with open('data/sources.json', encoding='utf-8') as handle:
        sources = json.load(handle)

    for source in sources:
        text = scrape_page(source['url'])
        output = RAW_DIR / f"{source['source_id']}.txt"
        output.write_text(text, encoding='utf-8')
        print(f'Saved: {output}')


if __name__ == '__main__':
    scrape_sources()
