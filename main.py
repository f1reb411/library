import requests
from pathlib import Path


def main():
    Path('books').mkdir(exist_ok=True)

    for book_number in range(1, 11):
        url = f'http://tululu.org/txt.php?id={book_number}'
        response = requests.get(url)
        response.raise_for_status()

        filename = f'id{book_number}.txt'

        with open(f'books/{filename}', 'w', encoding='utf-8') as file:
            file.write(response.text)


if __name__ == '__main__':
    main()
