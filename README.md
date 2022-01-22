# Парсер книг 

Программа скачивает книги с [tululu.org](https://tululu.org/). Taкже ко всем книгам скачиваются обложки и комментарии.

## Как установить

Python3 должен быть уже установлен. Затем используйте pip (или pip3, есть есть конфликт с Python2) для установки зависимостей:
```
pip install -r requirements.txt
```
## Запустить
```
python3 main.py --start_id=20 --finish_id=30
```
Если не указывать аргументы, будут скачаны книги по умолчанию(с 1 по 10)
