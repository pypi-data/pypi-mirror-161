# Copyright (c) 2021 T.Furukawa
# This software is released under the MIT License, see LICENSE.

from ..base import Config, Constant
from ..page import *
from ..language import *
from .page_iterator import *
from .parser import *


class BothIterator:

    def __init__(self, name = None, *, language = None):
        self.config = Config(name)
        self.name = self.config.name
        self.page_iterator = PageIterator(self.name)

        if language is None:
            self.language = Language.get_class(self.config.get_language(must = True))
        else:
            if language not in Constant.available_languages:
                raise ValueError(f"Language \"{language}\" is not supported.")
            else:
                self.language = Language.get_class(language)

    def __iter__(self):
        iter(self.page_iterator)
        return self

    def __next__(self):

        while True:
            page = next(self.page_iterator)
            item = Parser.page_to_class(page, language = self.language)

            if item is not None:
                return item
