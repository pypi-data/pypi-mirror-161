# Copyright (c) 2021 T.Furukawa
# This software is released under the MIT License, see LICENSE.

from .wscraper_language_error import *


class Language:

    @classmethod
    def get_class(cls, name):
        if name == "japanese":
            from .japanese import Japanese
            return Japanese
        elif name == "english":
            from .english import English
            return English
        else:
            raise WScraperLanguageError(f"Language `{name}` is not implemented.")
