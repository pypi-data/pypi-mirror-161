# Copyright (c) 2021 T.Furukawa
# This software is released under the MIT License, see LICENSE.

from .parser import *
from .entry_iterator import *


class ArticleIterator:

    def __init__(self, name = None, tagger = None, *, language = None, type = None):
        self.entry_iterator = EntryIterator(name = name, language = language)
        self.language = self.entry_iterator.both_iterator.language
        self.tagger = tagger
        self.type = type

    def __iter__(self):
        iter(self.entry_iterator)
        return self

    def __next__(self):

        while True:
            entry = next(self.entry_iterator)

            text = Parser.to_plain_text(entry.mediawiki, language = self.language)

            if self.tagger is None:
                article = text
            else:
                article = self.tagger(text)

            if article is not None:
                if self.type is None:
                    return article
                elif self.type == dict:
                    return {
                        "title": entry.title,
                        "article": article
                    }
                else:
                    raise NotImplementedError()
