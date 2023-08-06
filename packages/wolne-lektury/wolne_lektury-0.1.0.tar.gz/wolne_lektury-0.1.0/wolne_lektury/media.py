#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 23:18:39 2022

@author: krzysztof
"""

import os
import pandas as pd
from tqdm import tqdm
import urllib.request
import warnings

from . import urls
from .lists import get_books
from .enums import BookType, BookFormat


def _get_media_url(book_name: str, 
                   book_type: str, 
                   book_format: str):
    
    book_name = os.path.basename(book_name.rstrip("/"))
    book_name = f"{book_name}.{book_format}"
    return os.path.join(urls.MAIN, 
                        urls.MEDIA,
                        book_type,
                        book_format,
                        book_name)


def _download_file(url: str, output_dir: str):
    try:
        output_path = os.path.basename(url.rstrip("/"))
        output_path = os.path.join(output_dir, output_path)
        urllib.request.urlretrieve(url, output_path) 
    except:
        warning = f"Cannot download {url}"
        warnings.warn(warning)


def download(output_dir: str,
             book_list: pd.DataFrame = None,
             book: str = None,
             author: str = None, 
             epoch: str = None, 
             genre: str = None,
             kind: str = None, 
             language: str = None,
             book_type: str = BookType.BOOK,
             book_format: str = BookFormat.TXT):
    """Download files from wolnelektury.com
    
    For parameters such as book, author, epoch, genre and kind you can 
    pass slugified or normal strings, e.g. 'Adam Mickiewicz' or 'adam-mickiewicz'.
    In the first case, the string is automatically slugified behind the scene.
    
    If you pass a value to the 'language' argument, it will take an additional time
    to fetch the data. It's because the we have to call the Wolne Lektury API
    individually for each book in the loop to retrieve such data.    
    
    Bear in mind that lnaguage abbreviation may have unexpected format, e.g.
    'pol' for Polish language (instead of 'pl', as usual).
    
    Parameters
    ----------
    output_dir: str
        A directory, the files will be saved in
    book_list: pd.DataFrame
        A pandas DataFrame with a list of books fetched with get_books function.
    book: str
        The book title. If specified, you should not pass any other options.
    author: str
        A selected author. Can be combined with other arguments (excluding book_list and book).
    epoch: str
        A selected epoch. Can be combined with other arguments (excluding book_list and book).
    genre: str
        A seleted genre. Can be combined with other arguments (excluding book_list and book).
    kind: str
        A selected kind. Can be combined with other arguments (excluding book_list and book).
    book_type: BookType
        An enum value of class BookType: BOOK, AUDIOBOOK or DAISY.
    book_format: BookType
        An enum value of class BookType: TXT, PDF, EPUB, MOBI, FB2, MP3 or OGG.
        It must match the book_type, i.e. FB2, MP3 and OGG are for BookType.AUDIOBOOK
        and BookType.DAISY.   

    Examples
    -------
    >>> import os
    >>> import wolne_lektury as wl
    >>> os.mkdir("out")
    >>> 
    >>> wl.download(output_dir="out",
    >>>             author="Henryk Sienkiewicz", 
    >>>             language="pol",
    >>>             book_type=wl.BookType.BOOK,
    >>>             book_format=wl.BookFormat.PDF) 
    >>> type(sienkiewicz)       
    collections.OrderedDict
    >>> print(os.listdir("out")[0:5])    
    ['sienkiewicz-wesele.pdf', 'sienkiewicz-na-olimpie.pdf', 'potop-tom-pierwszy.pdf', 
     'sienkiewicz-przygoda-arystoklesa.pdf', 'krzyzacy-tom-drugi.pdf']
    """
    
    if not book_list:
        book_list = get_books(
                book=book,
                author=author,
                epoch=epoch,
                genre=genre,
                kind=kind,
                language=language
            )
    
    book_url_list = book_list['url'].tolist()
    
    for book in tqdm(book_url_list):
        url = _get_media_url(book, 
                             book_type = book_type, 
                             book_format = book_format)
        _download_file(url, output_dir)
        
        
if __name__ == '__main__':
    download("out", author="Adam Mickiewicz")
    
