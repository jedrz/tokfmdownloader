#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import urllib2

import progbar


def download_file(url, filename):
    """Pobiera plik, wyświetlajac aktualny stan pobierania w postaci
    progressbara.
    """
    outfile = open(filename, "wb")
    urlfile = urllib2.urlopen(url)
    filesize = int(urlfile.headers.get("Content-Length"))

    # ile bajtów pobieram pobieram w każdym obiegu pętli
    step = 1024 * 64

    progressbar = progbar.ProgressBar(filesize + step, 50)
    progbar.cone()
    def print_progbar():
        progbar.ctwo()
        sys.stdout.write("{0}".format(progressbar))
        progbar.cthree()
    print_progbar()
    i = 0
    while True:
        bytes = urlfile.read(step)
        outfile.write(bytes)
        if bytes == "":
            progressbar.update(filesize + step)
            print_progbar()
            break
        i += step
        progressbar.update(i)
        print_progbar()

    sys.stdout.write("\n")
    urlfile.close()
    outfile.close()
