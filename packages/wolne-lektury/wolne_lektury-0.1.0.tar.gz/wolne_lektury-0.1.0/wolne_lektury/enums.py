#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 00:38:24 2022

@author: krzysztof
"""

from enum import Enum

class BookType(str, Enum):
    BOOK      = "book"
    AUDIOBOOK = "audiobook"
    DAISY     = "daisy"


class BookFormat(str, Enum):
    TXT  = "txt"
    PDF  = "pdf"
    EPUB = "epub"
    MOBI = "mobi"
    FB2  = "fb2"
    MP3 = "mp3"
    OGG = "ogg" # Ogg Vorbis