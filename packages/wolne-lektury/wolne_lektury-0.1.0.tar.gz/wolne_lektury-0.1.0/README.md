# wolne_lektury <img src='img/wl_logo.png' align="right" height="139" />
> An unofficial REST API client for [Wolne Lektury](wolnelektury.pl) 

## Installation

You can install this library from *PyPI*

```bash
pip install wolne_lektury
```

or from the GitHub repo:
 
```bash
pip install git+https://github.com/krzjoa/wolne_lektury.git
```

## Usage 
```python
import wolne_lektury as wl

# Query is automatically slugified, so you can type author names in natural language
wl.get_books(authors = "Juliusz Słowacki")
wl.get_books(authors = "adam-mickiewicz")

# Use more complex queries. You can specify language as well
wl.get_books(epoch="Romantyzm", genre="Powieść")
wl.get_books(epoch="Modernizm", kind="Liryka", language="pol")

# Get lists of authors, epochs, genres, kinds, themes and collenctions
wl.get_authors()
wl.get_epochs()
wl.get_genres()
wl.get_kinds()
wl.get_themes()
wl.get_collections()

# Retrieve full textes or download them as files
books = wl.get_texts(author="Ignacy Krasicki")
print(list(books.values())[4][:60])
'Dwa żółwie\r\n\r\n\r\n\r\nNie żałując sił własnych i ciężkiej fatygi'

wl.download("output_dir", author="Henryk Sienkiewicz", book_format=wl.BookFormat.PDF)

```
