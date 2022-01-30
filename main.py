import argparse
import os
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def create_parser():
    parser = argparse.ArgumentParser(description='Программа скачивает книги с сайта tululu.org')
    parser.add_argument('--start_id', type=int, default=1)
    parser.add_argument('--finish_id', type=int, default=10)
    return parser.parse_args()


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def extract_book(book_id, response, title, folder='books/'):
    filename = f'{book_id}. {title}.txt'
    safe_filename = sanitize_filename(filename)
    filepath = os.path.join(folder, safe_filename)

    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(response.text)
    return safe_filename


def download_image(url, folder='images/'):
    response = requests.get(url)
    response.raise_for_status()

    image_name = str(urlsplit(url).path.split('/')[-1])
    filepath = os.path.join(folder, image_name)

    with open(filepath, 'wb') as file:
        file.write(response.content)

    return filepath


def download_book_comments(book_id, author, soup, folder='comments/'):
    comments_tag = soup.find_all('div', class_='texts')
    comments = ''
    for comment in comments_tag:
        comments += comment.find('span', class_='black').text + ' '

    filename = f'{book_id}. {author}'
    filepath = os.path.join(folder, filename)

    if comments:
        with open(filepath, 'w') as file:
            file.write(comments)

    return comments


def parse_book_page(book_url, soup):
    title, author = soup.find('table').find('h1').text.split('::')

    genre_tag = soup.find('span', class_='d_book').find_all('a')

    image_tag = soup.find('div', class_='bookimage').find('img')['src']

    book_parsed_page = {
        'title': title.strip(),
        'author': author.strip(),
        'genre': [genre.text for genre in genre_tag],
        'image_url': urljoin(book_url, image_tag)
    }

    return book_parsed_page


def main():
    Path('books').mkdir(exist_ok=True)
    Path('images').mkdir(exist_ok=True)
    Path('comments').mkdir(exist_ok=True)

    parser = create_parser()

    for book_id in range(parser.start_id, parser.finish_id + 1):
        book_url = 'http://tululu.org/txt.php'
        parse_url = f'http://tululu.org/b{book_id}'

        response = requests.get(book_url, params={'id': book_id})
        parse_response = requests.get(parse_url)

        try:
            response.raise_for_status()
            check_for_redirect(response)
            parse_response.raise_for_status()
        except (requests.HTTPError, requests.ConnectionError):
            continue

        soup = BeautifulSoup(parse_response.text, 'lxml')
        book_info = parse_book_page(book_url, soup)

        extract_book(book_id, response, book_info['title'])
        download_image(book_info['image_url'])
        download_book_comments(book_id, book_info['author'], soup)


if __name__ == '__main__':
    main()
