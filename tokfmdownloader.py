#!/usr/bin/env python
# -*- coding: utf-8 -*-

# do działania potrzebna biblioteka mutagen (edycja tagów mp3)

"""Skrypt pobiera pliki mp3 (podcasty?) z radia TOK FM

Pliki są zapisywane w formacie: przedrostek-data, np.
ekg-05_02_03.mp3

Użycie:
    <adres do rss> <ścieżka do zapisu plików> <przedrostek>
    przedrostek oznacza jak ma się nazywać początek pobieranych nazw
    plików (nie trzeba podawać myślnika na końcu - zostanie
    automatycznie dodany)
"""


import sys
import os
import urllib2
from xml.dom import minidom

from mutagen.easyid3 import EasyID3

import download


class TokFmPodcastsParser(object):
    """Ta klasa jest przydatna do pobierania informacji oraz plików
    mp3 z rssa radia TokFM.
    """

    def __init__(self, xmlfile):
        # dokument xml
        self.xmldoc = minidom.parse(xmlfile)
        # lista audycji
        self.items = self.xmldoc.getElementsByTagName("item")
        # słownik miesięcy, potrzebny do konwersji daty
        self.months = {
                "Jan": "01",
                "Feb": "02",
                "Mar": "03",
                "Apr": "04",
                "May": "05",
                "Jun": "06",
                "Jul": "07",
                "Aug": "08",
                "Sep": "09",
                "Oct": "10",
                "Nov": "11",
                "Dec": "12"
        }

    def get_url(self, item):
        """Zwraca url aktualnej audycji"""
        enclosure = item.getElementsByTagName("enclosure")[0]
        url = enclosure.getAttribute("url")
        return url

    def get_author(self, item):
        """Zwraca tekst ze znacznika 'itunes:author' zawierający
        informację o autorze z aktualnej audycji.
        """
        author_tag = item.getElementsByTagName("itunes:author")[0]
        author = author_tag.firstChild.data
        return author

    def get_title(self, item):
        """Zwraca tytuł ze znacznika 'title' z aktualnej audycji"""
        title_tag = item.getElementsByTagName("title")[0]
        title = title_tag.firstChild.data
        return title

    def get_date(self, item):
        """Zwraca listę zawierającą datę podcastu

        Elementy listy: dzień, miesiąc, rok, format dd,
        mm, rrrr.
        """
        pubdate = item.getElementsByTagName("pubDate")[0]
        # data typu Thu, 30 Jul 2009 11:22:00 +0200
        date = pubdate.firstChild.data
        # lista z dniem, miesiącem, rokiem
        ldate = date.split()[1:4]
        ldate[1] = self.months[ldate[1]]
        return ldate

    def get_current(self):
        """Parsuje dane najnowszej audycji.
        Zwraca słownik zawierający klucze url, title, author, date
        """
        item = self.items[0]
        data = {}
        data["url"] = self.get_url(item)
        data["title"] = self.get_title(item)
        data["author"] = self.get_author(item)
        data["date"] = self.get_date(item)
        return data

    def get_all(self):
        """Parsuje informacje o wszystkich audycjach w rss.
        Zwraca listę słowników zawierających klucze url, title,
        author, date.
        """
        data = []
        for item in self.items:
            d = {}
            d["url"] = self.get_url(item)
            d["title"] = self.get_title(item)
            d["author"] = self.get_author(item)
            d["date"] = self.get_date(item)
            data.append(d)
        return data

    def get_items(self):
        return self.items

    def get_current_item(self):
        return self.items[0]


def edit_id3(file, title, album):
    """Funkcja edytuje tagi mp3 za pomocą biblioteki mutagen

    Zmienia tag album oraz zmienia tag title na podany w argumencie.
    """
    audio = EasyID3(file)
    audio["album"] = album
    audio["title"] = title
    audio.save()


def download_all(url, path, prefix, ext=".mp3"):
    """Pobiera wszystkie podcasty

    Argumenty:
     url - adres do rss
     path - ścieżka do zapisu plików
     prefix - początek nazwy plku
     ext - rozszerzenie pliku (chyba zawsze .mp3)
    Następnie modyfikuje tagi mp3:
     - zmienia tag album na miesiąc i rok
     - zmiena tag title na datę podcastu
    Przy pobieraniu plików korzysta z modułu download, który
    wyświetla także pasek postępu.
    """
    try:
        usock = urllib2.urlopen(url)
    except IOError:
        print("Nieprawidłowy adres lub błąd połączenia")
        sys.exit(1)
    parser = TokFmPodcastsParser(usock)
    data = parser.get_all()
    for d in data:
        filename = prefix + "-" + "_".join(d["date"]) + ext
        file_path = os.path.join(path, filename)
        if os.path.isfile(file_path):
            print("{0} istnieje, pomijam go".format(filename))
        else:
            print("{0}".format(filename))
            download.download_file(d["url"], file_path)
            # zmieniam tag album na miesiąc i rok, ustawiam
            # tytuł na datę podcastu
            title = ".".join(d["date"])
            album = ".".join(d["date"][1:])
            edit_id3(file_path, title, album)


def download_current(url, path, prefix, ext=".mp3"):
    """Pobiera aktualny podcast"""
    try:
        usock = urllib2.urlopen(url)
    except IOError:
        print("Nieprawidłowy adres lub błąd połączenia")
        sys.exit(1)
    parser = TokFmPodcastsParser(usock)
    data = parser.get_current()
    filename = prefix + "-" + "_".join(data["date"]) + ext
    file_path = os.path.join(path, filename)
    if os.path.isfile(file_path):
        print("{0} istnieje, pomijam go".format(filename))
    else:
        print("{0}".format(filename))
        download.download_file(data["url"], file_path)
        # zmieniam tag album na miesiąc i rok, ustawiam
        # tytuł na datę podcastu
        title = ".".join(data["date"])
        album = ".".join(data["date"][1:])
        edit_id3(file_path, title, album)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage {0} <url to rss from TokFm> <path to save files> "
                "<file prefix>".format(sys.argv[0]))
        sys.exit(1)
    download_all(sys.argv[1], os.path.expanduser(sys.argv[2]), sys.argv[3])
    print("Koniec")
