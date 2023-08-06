#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 23 17:19:37 2022

@author: krzysztof
"""

import requests
import pandas as pd
import os
from slugify import slugify
from tqdm import tqdm
from typing import Union

from . import urls

class ItemNotFound(Exception):
    def __init__(self):
        super().__init__("Searched item not found")


def _get_list(url: str, normalize: bool = False) -> pd.DataFrame:
    url = os.path.join(urls.API, url)
    response = requests.get(url).json()
    
    if response == {'detail': 'Nie znaleziono.'}:
        raise ItemNotFound()
    
    if normalize:
        response = pd.json_normalize(response)
    return pd.DataFrame.from_records(response)

def _book_info(book: str):
    url = os.path.join(urls.API, urls.BOOKS, book)
    response = requests.get(url).json()
    return response

def _book_lang(book: str):
    return _book_info(book)['language']  


def _q(path_type: str, query: str):
    """Prepare query"""
    return "" if not query else os.path.join(path_type, slugify(query))


def _chained_book_query(book: str = None,
                        author: str = None, 
                        epoch: str = None, 
                        genre: str = None,
                        kind: str = None, 
                        language: Union[str, bool] = None,
                        book_type: str = 'books'):
    
    available_book_types = [urls.BOOKS, urls.AUDIOBOOKS, urls.DAISY]
    
    if book_type not in available_book_types:
        raise ValueError(f"You passed {book_type} as book type, which is none" \
                         f"of {*available_book_types,}")
    
    if book:
        query = os.path.join(urls.BOOKS, slugify(book))
        one_book = True
    else:
        query = os.path.join(
                _q(urls.AUTHORS, author),
                _q(urls.EPOCHS, epoch),
                _q(urls.GENRES, genre),
                _q(urls.KINDS, kind),
                #_q(urls.THEMES, theme),
                #_q(urls.COLLECTIONS, collection),
                book_type
            )
        one_book = False
    
    output = _get_list(query, normalize=one_book)
    
    if language and not one_book:
        print("You need langauge column, so additional info has to be retrieved")
        langs = [_book_lang(b) for b in tqdm(output.slug.tolist())]
        output = output.assign(language = langs)
        
    if type(language) == str:
        output = output.query("language == @language")
    
    return output
    
    
def get_books(book: str = None,
              author: str = None, 
              epoch: str = None, 
              genre: str = None,
              kind: str = None, 
              language: Union[str, bool] = None) -> pd.DataFrame:
    """Get list of books
    
    For parameters such as book, author, epoch, genre and kind you can 
    pass slugified or normal strings, e.g. 'Adam Mickiewicz' or 'adam-mickiewicz'.
    In the first case, the string is automatically slugified behind the scene.
    
    If you pass a value to the 'language' argument, it will take an additional time
    to fetch the data. It's because the we have to call the Wolne Lektury API
    individually for each book in the loop to retrieve such data.  
    
    Bear in mind that lnaguage abbreviation may have unexpected format, e.g.
    'pol' for Polish language (instead of 'pl', as usual).
    
    References
    ----------
    https://wolnelektury.pl/api/
    
    Parameters
    ----------
    
    book: str
        A title of a particular book.
    author: str
        Author name
    epoch: str
        Epoch name
    genre: str 
        Genre name
    kind: str
        Kind name
    language: str or bool
        Fetch information about language or select a language. 
    
    Returns
    -------
    pd.DataFrame
        A pandas DataFrame with list of books
    
    Examples
    --------
    >>> import wolne_lektury as wl
    >>> # Fetching one book
    >>> book = wl.get_books(book="Pan Tadeusz") 
    >>> print(book.columns)
    Index(['title', 'url', 'language', 'epochs', 'genres', 'kinds', 'authors',
           'translators', 'children', 'parent', 'preview', 'epub', 'mobi', 'pdf',
           'html', 'txt', 'fb2', 'xml', 'media', 'audio_length', 'cover_color',
           'simple_cover', 'cover_thumb', 'cover', 'simple_thumb', 'isbn_pdf',
           'isbn_epub', 'isbn_mobi', 'fragment_data.title', 'fragment_data.html'],
          dtype='object')
    >>> # Add information about the language
    >>> mickiewicz_books = wl.get_books(author="Adam Mickiewicz", language=True)
    >>> print(mickiewicz_books.shape)
    (158, 16)
    >>> # Get books in a selected langaue
    >>> mickiewicz_books_pl = wl.get_books(author="Adam Mickiewicz", language="pol")
    >>> print(mickiewicz_books_pl.shape)
    (127, 16)
    >>> # A more complex query
    >>> books = wl.get_books(epoch="Romantyzm", genre="Powieść")
    >>> print(books.title.head(3))
    0               Trzej muszkieterowie
    1    Trzej muszkieterowie, tom drugi
    2                       Tylko grajek
    Name: title, dtype: object
    """
    return _chained_book_query(book, author, epoch, genre, 
                               kind, language, 
                               book_type=urls.BOOKS)

def get_audiobooks(book: str = None, 
                   author: str = None, 
                   epoch: str = None, 
                   genre: str = None,
                   kind: str = None, 
                   language: Union[str, bool] = None) -> pd.DataFrame:
    """Get list of audiobooks
    
    For parameters such as book, author, epoch, genre and kind you can 
    pass slugified or normal strings, e.g. 'Adam Mickiewicz' or 'adam-mickiewicz'.
    In the first case, the string is automatically slugified behind the scene.
    
    If you pass a value to the 'language' argument, it will take an additional time
    to fetch the data. It's because the we have to call the Wolne Lektury API
    individually for each book in the loop to retrieve such data.    
    
    Bear in mind that lnaguage abbreviation may have unexpected format, e.g.
    'pol' for Polish language (instead of 'pl', as usual).
    
    References
    ----------
    https://wolnelektury.pl/api/
    
    Parameters
    ----------
    
    book: str
        A title of a particular book.
    author: str
        Author name
    epoch: str
        Epoch name
    genre: str 
        Genre name
    kind: str
        Kind name
    language: str or bool
        Fetch information about language or select a language. 
    
    Returns
    -------
    pd.DataFrame
        A pandas DataFrame with list of books
    
    Examples
    --------
    >>> import wolne_lektury as wl
    >>> # Fetching one book
    >>> book = wl.get_audiobooks(book="Pan Tadeusz") 
    >>> print(book.columns)
    Index(['title', 'url', 'language', 'epochs', 'genres', 'kinds', 'authors',
           'translators', 'children', 'parent', 'preview', 'epub', 'mobi', 'pdf',
           'html', 'txt', 'fb2', 'xml', 'media', 'audio_length', 'cover_color',
           'simple_cover', 'cover_thumb', 'cover', 'simple_thumb', 'isbn_pdf',
           'isbn_epub', 'isbn_mobi', 'fragment_data.title', 'fragment_data.html'],
          dtype='object')
    >>> # Add information about the language
    >>> mickiewicz_books = wl.get_audiobooks(author="Adam Mickiewicz", language=True)
    >>> print(mickiewicz_books.shape)
    (32, 16)
    >>> # Get books in a selected langaue
    >>> mickiewicz_books_pl = wl.get_audiobooks(author="Adam Mickiewicz", language="pol")
    >>> print(mickiewicz_books_pl.shape)
    (32, 16)
    >>> # A more complex query
    >>> books = wl.get_audiobooks(epoch="Romantyzm", genre="Powieść")
    >>> print(books.title.head(3))
    0     Bank Nucingena
    1          Córka Ewy
    2    Eugenia Grandet
    Name: title, dtype: object
    """
    return _chained_book_query(book, author, epoch, genre, 
                               kind, language, 
                               book_type=urls.AUDIOBOOKS)

def get_daisy(book: str = None,
              author: str = None, 
              epoch: str = None, 
              genre: str = None,
              kind: str = None, 
              language: Union[str, bool] = None) -> pd.DataFrame:
    """Get list of books in DAISY version
    
    For parameters such as book, author, epoch, genre and kind you can 
    pass slugified or normal strings, e.g. 'Adam Mickiewicz' or 'adam-mickiewicz'.
    In the first case, the string is automatically slugified behind the scene.
    
    If you pass a value to the 'language' argument, it will take an additional time
    to fetch the data. It's because the we have to call the Wolne Lektury API
    individually for each book in the loop to retrieve such data.    
    
    Bear in mind that lnaguage abbreviation may have unexpected format, e.g.
    'pol' for Polish language (instead of 'pl', as usual).
    
    References
    ----------
    https://wolnelektury.pl/api/
    
    Parameters
    ----------
    
    book: str
        A title of a particular book.
    author: str
        Author name
    epoch: str
        Epoch name
    genre: str 
        Genre name
    kind: str
        Kind name
    language: str or bool
        Fetch information about language or select a language. 
    
    Returns
    -------
    pd.DataFrame
        A pandas DataFrame with list of books
    
    Examples
    --------
    >>> import wolne_lektury as wl
    >>> # Fetching one book
    >>> book = wl.get_daisy(book="Pan Tadeusz") 
    >>> print(book.columns)
    Index(['title', 'url', 'language', 'epochs', 'genres', 'kinds', 'authors',
           'translators', 'children', 'parent', 'preview', 'epub', 'mobi', 'pdf',
           'html', 'txt', 'fb2', 'xml', 'media', 'audio_length', 'cover_color',
           'simple_cover', 'cover_thumb', 'cover', 'simple_thumb', 'isbn_pdf',
           'isbn_epub', 'isbn_mobi', 'fragment_data.title', 'fragment_data.html'],
          dtype='object')
    >>> # Add information about the language
    >>> mickiewicz_books = wl.get_daisy(author="Adam Mickiewicz", language=True)
    >>> print(mickiewicz_books.shape)
    (23, 16)
    >>> # Get books in a selected langaue
    >>> mickiewicz_books_pl = wl.get_daisy(author="Adam Mickiewicz", language="pol")
    >>> print(mickiewicz_books_pl.shape)
    (23, 16)
    >>> # A more complex query
    >>> books = wl.get_daisy(epoch="Romantyzm", genre="Powieść")
    >>> print(books.title.head(3))
    0     Bank Nucingena
    1          Córka Ewy
    2    Eugenia Grandet
    Name: title, dtype: object
    """
    return _chained_book_query(book, author, epoch, genre, 
                               kind, language, 
                               book_type=urls.DAISY)


# TODO: define specific author, epoch etc.

def get_authors() -> pd.DataFrame:
    """Get list of authors
    
    Returns
    -------
    pd.DataFrame
        A list of available authors
        
    References
    ----------
    https://wolnelektury.pl/api/
    
    Examples
    --------
    >>> import wolne_lektury as wl
    >>> wl.get_authors()
                                                   url  ...                      slug
    0    https://wolnelektury.pl/katalog/autor/abraham-...  ...     abraham-govaerts
    1    https://wolnelektury.pl/katalog/autor/abraham-...  ...      abraham-hondius
    2    https://wolnelektury.pl/katalog/autor/abraham-...  ...       abraham-mignon
    3    https://wolnelektury.pl/katalog/autor/adam-asnyk/  ...           adam-asnyk
    4    https://wolnelektury.pl/katalog/autor/adam-chm...  ...     adam-chmielowski
    ..                                                 ...  ...                  ...
    651  https://wolnelektury.pl/katalog/autor/zygmunt-...  ...    zygmunt-krasinski
    652  https://wolnelektury.pl/katalog/autor/zygmunt-...  ...    zygmunt-milkowski
    653  https://wolnelektury.pl/katalog/autor/zygmunt-...  ...   zygmunt-przybylski
    654  https://wolnelektury.pl/katalog/autor/zygmunt-...  ...        zygmunt-vogel
    655  https://wolnelektury.pl/katalog/autor/zygmunt-...  ...  zygmunt-waliszewski
     
    [656 rows x 4 columns]
    """
    return _get_list(urls.AUTHORS)


def get_epochs() -> pd.DataFrame:
    """Get list of epochs
    
    Returns
    -------
    pd.DataFrame
        A list of available epochs
        
    References
    ----------
    https://wolnelektury.pl/api/
    
    Examples
    --------
    >>> import wolne_lektury as wl
    >>> wl.get_epochs().head(5)
                                                      url  ...                           slug
    0   https://wolnelektury.pl/katalog/epoka/akademizm/  ...                      akademizm
    1       https://wolnelektury.pl/katalog/epoka/barok/  ...                          barok
    2  https://wolnelektury.pl/katalog/epoka/dwudzies...  ...  dwudziestolecie-miedzywojenne
    3  https://wolnelektury.pl/katalog/epoka/epoka-st...  ...           epoka-stanislawowska
    4       https://wolnelektury.pl/katalog/epoka/gotyk/  ...                          gotyk
     
    [5 rows x 4 columns]
    """
    return _get_list(urls.EPOCHS)


def get_genres() -> pd.DataFrame:
    """Get list of genres
    
    Returns
    -------
    pd.DataFrame
        A list of available genres
        
    References
    ----------
    https://wolnelektury.pl/api/
    
    Examples
    --------
    >>> import wolne_lektury as wl
    >>> wl.get_genres().head(5)
                                                      url  ...          slug
    0   https://wolnelektury.pl/katalog/gatunek/aforyzm/  ...      aforyzm
    1       https://wolnelektury.pl/katalog/gatunek/akt/  ...          akt
    2  https://wolnelektury.pl/katalog/gatunek/akt-pr...  ...   akt-prawny
    3  https://wolnelektury.pl/katalog/gatunek/alegoria/  ...     alegoria
    4  https://wolnelektury.pl/katalog/gatunek/anakre...  ...  anakreontyk
     
    [5 rows x 4 columns]
    """
    return _get_list(urls.GENRES)


def get_kinds() -> pd.DataFrame:
    """Get list of kinds
    
    Returns
    -------
    pd.DataFrame
        A list of available kinds
        
    References
    ----------
    https://wolnelektury.pl/api/
    
    Examples
    --------
    >>> import wolne_lektury as wl
    >>> wl.get_kinds().head(5)
                                                      url  ...         slug
    0  https://wolnelektury.pl/katalog/rodzaj/bodzettov/  ...   bodzettov
    1   https://wolnelektury.pl/katalog/rodzaj/ceramika/  ...    ceramika
    2     https://wolnelektury.pl/katalog/rodzaj/dramat/  ...      dramat
    3      https://wolnelektury.pl/katalog/rodzaj/epika/  ...       epika
    4  https://wolnelektury.pl/katalog/rodzaj/fotogra...  ...  fotografia
     
    [5 rows x 4 columns]
    """
    return _get_list(urls.KINDS)


def get_themes() -> pd.DataFrame:
    """Get list of themes
    
    Returns
    -------
    pd.DataFrame
        A list of available themes
        
    References
    ----------
    https://wolnelektury.pl/api/
    
    Examples
    --------
    >>> import wolne_lektury as wl
    >>> wl.get_themes().head(5)
                                                      url  ...  slug
    0    https://wolnelektury.pl/katalog/motyw/aktor/  ...    aktor
    1  https://wolnelektury.pl/katalog/motyw/aktorka/  ...  aktorka
    2  https://wolnelektury.pl/katalog/motyw/alkohol/  ...  alkohol
    3  https://wolnelektury.pl/katalog/motyw/ambicja/  ...  ambicja
    4  https://wolnelektury.pl/katalog/motyw/ameryka/  ...  ameryka
     
    [5 rows x 4 columns]
    """
    return _get_list(urls.THEMES)


def get_collections() -> pd.DataFrame:
    """Get list of collections
    
    Returns
    -------
    pd.DataFrame
        A list of available collections
        
    References
    ----------
    https://wolnelektury.pl/api/
    
    Examples
    --------
    >>> import wolne_lektury as wl
    >>> wl.get_collections().head(5)
                                                 url  ...                      title
    0  https://wolnelektury.pl/katalog/lektury/basnie...  ...    Baśnie, bajki, bajeczki
    1  https://wolnelektury.pl/katalog/lektury/biblio...  ...      Biblioteczka antyczna
    2       https://wolnelektury.pl/katalog/lektury/boy/  ...          Biblioteczka Boya
    3  https://wolnelektury.pl/katalog/lektury/biblio...  ...  Biblioteczka filozoficzna
    4  https://wolnelektury.pl/katalog/lektury/biblio...  ...       Biblioteczka naukowa
     
    [5 rows x 3 columns]
    """
    return _get_list(urls.COLLECTIONS)


if __name__ == '__main__':
    book = get_books(book="Pan Tadeusz") 
    mickiewicz_books = get_books(author="Adam Mickiewicz", language="pol")
    # books = get_books(author="Juliusz Słowacki") 
    # print(get_books(author="Juliusz Słowacki"))
    