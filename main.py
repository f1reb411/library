import os
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_txt(url, filename, folder='books/'):
    response = requests.get(url)
    response.raise_for_status()
    safe_filename = sanitize_filename(filename)
    filepath = os.path.join(folder, safe_filename)
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(response.text)
    return filepath


def parse_book_title(book_id, soup):
    tag = soup.find('table').find('h1').text
    book = tag.split('::')
    return f'{book_id}. {book[0].strip()}.txt'


def parse_book_author(soup):
    tag = soup.find('table').find('h1').text
    book = tag.split('::')
    return book[1].strip()


def main():
    Path('books').mkdir(exist_ok=True)

    for book_id in range(1, 11):
        url = f'http://tululu.org/txt.php?id={book_id}'
        book_url = f'http://tululu.org/b{book_id}'
        response = requests.get(url)
        response.raise_for_status()

        try:
            check_for_redirect(response)
        except requests.HTTPError:
            continue

        response = requests.get(book_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')

        download_txt(url, parse_book_title(book_id, soup))


if __name__ == '__main__':
    main()
