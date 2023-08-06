# Copyright (c) 2021 T.Furukawa
# This software is released under the MIT License, see LICENSE.


class LanguageBase:

    @classmethod
    def escape_decode(cls, string):
        return string.replace("&amp;", "&")

    @classmethod
    def extract_category(cls, link):
        category = "Category:"

        if link.startswith(category):
            return link[len(category):].rstrip("\u200e")
        else:
            return None
