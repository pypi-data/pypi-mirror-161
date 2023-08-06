# Copyright (c) 2021 T.Furukawa
# This software is released under the MIT License, see LICENSE.

from ..page import *
from .both_iterator import *


class EntryIterator:

    def __init__(self, name = None, *, language = None):
        self.both_iterator = BothIterator(name, language = language)

    def __iter__(self):
        iter(self.both_iterator)
        return self

    def __next__(self):

        while True:
            page = next(self.both_iterator)

            if page is not None and type(page) == Entry:
                return page
