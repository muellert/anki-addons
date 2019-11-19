# -*- mode: python; coding: utf-8 -*-
#
# Copyright © 2014–15 Roland Sieker <ospalh@gmail.com>
#
# License: GNU AGPL, version 3 or later;
# http://www.gnu.org/copyleft/agpl.html


"""
Download German pronunciations from  Collins Dictionary.
"""

from ..download_entry import Action
from .collins import CollinsDownloader


class CollinsGermanDownloader(CollinsDownloader):
    """Download German audio from Collins Dictionary."""
    def __init__(self):
        CollinsDownloader.__init__(self)
        self.url \
            = 'http://www.collinsdictionary.com/dictionary/german-english/'
        self.lang = 'de'
        self.lang_code = '/de_/'
        self.icon_url = self.url
        self.extras = dict(Source="Collins German")
        self.action = Action.Delete  # We have enough sources from Germany

    # Use CollinsDownloader for the real work.
