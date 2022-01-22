import argparse
import os
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def create_parser():
    parser = argparse.ArgumentParser(description='Программа скачивает книги с сайта tululu.org')
    parser.add_argument('start_id', type=int)
    parser.add_argument('finish_id', type=int)
    return parser.parse_args()


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
    return safe_filename


def parse_book_author(soup):
    tag = soup.find('table').find('h1').text
    book = tag.split('::')
    return book[1].strip()


def download_image(book_url, soup, folder='images/'):
    url = parse_book_image(book_url, soup)
    response = requests.get(url)
    response.raise_for_status()

    image_name = str(urlsplit(url).path.split('/')[-1])
    filepath = os.path.join(folder, image_name)

    with open(filepath, 'wb') as file:
        file.write(response.content)

    return filepath


def download_book_comments(book_id, soup, folder='comments/'):
    book_author = parse_book_author(soup)

    comments_tag = soup.find_all('div', class_='texts')
    comments = ''
    for comment in comments_tag:
        comments += comment.find('span', class_='black').text + ' '

    filename = f'{book_id}. {book_author}'
    filepath = os.path.join(folder, filename)

    if comments:
        with open(filepath, 'w') as file:
            file.write(comments)

    return comments


def parse_book_image(book_url, soup):
    book_image = soup.find('div', class_='bookimage').find('img')['src']
    book_image1 = urljoin(book_url, book_image)
    return book_image1


def parse_book_genre(soup):
    genre_tag = soup.find('span', class_='d_book').find_all('a')
    genres = []
    for genre in genre_tag:
        genres.append(genre.text)
    return genres


def parse_book_title(book_id, soup):
    tag = soup.find('table').find('h1').text
    book = tag.split('::')
    return f'{book_id}. {book[0].strip()}.txt'


def parse_book_page(book_id, book_url, soup):

    book_parsed_page = {
        'title': parse_book_title(book_id, soup),
        'genre': parse_book_genre(soup),
        'author': parse_book_author(soup),
        'image': parse_book_image(book_url, soup)
    }

    return book_parsed_page


def main():
    Path('books').mkdir(exist_ok=True)
    Path('images').mkdir(exist_ok=True)
    Path('comments').mkdir(exist_ok=True)

    parser = create_parser()
    print(parser.start_id, parser.finish_id)

    for book_id in range(parser.start_id, parser.finish_id + 1):
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
        download_image(book_url, soup)
        download_book_comments(book_id, soup)


if __name__ == '__main__':
    main()
