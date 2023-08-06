# Copyright (c) 2021 T.Furukawa
# This software is released under the MIT License, see LICENSE.

from .parser import *
from .entry_iterator import *


class ParagraphIterator:

    def __init__(self, name = None, tagger = None, *, language = None, type = None):
        self.entry_iterator = EntryIterator(name = name, language = language)
        self.language = self.entry_iterator.both_iterator.language
        self.tagger = tagger
        self.type = type
        self.current_title = None
        self.stock = []

    def __iter__(self):
        iter(self.entry_iterator)
        return self

    def __next__(self):

        while True:

            if len(self.stock) == 0:
                entry = next(self.entry_iterator)
                self.current_title = entry.title
                self.stock = Parser.to_paragraphs(entry.mediawiki, language = self.language)
                continue

            item = self.stock.pop(0)
            subtitle, text = item

            if self.tagger is None:
                paragraph = text
            else:
                paragraph = self.tagger(text)

            if paragraph is not None:
                if self.type is None:
                    return paragraph
                elif self.type == dict:
                    return {
                        "page_title": self.current_title,
                        "paragraph_title": subtitle,
                        "paragraph": paragraph
                    }
                else:
                    raise NotImplementedError()
