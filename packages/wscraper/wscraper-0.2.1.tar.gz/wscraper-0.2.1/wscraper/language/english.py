# Copyright (c) 2021 T.Furukawa
# This software is released under the MIT License, see LICENSE.

import re

from .language_base import *


class English(LanguageBase):

    exclusive_title = [
        "Media",
        "Special",
        "Talk",
        "User",
        "User talk",
        "Wikipedia",
        "Wikipedia talk",
        "File",
        "File talk",
        "MediaWiki",
        "MediaWiki talk",
        "Template",
        "Template talk",
        "Help",
        "Help talk",
        "Category",
        "Category talk",
        "Portal",
        "Portal talk",
        "Book",
        "Book talk",
        "Draft",
        "Draft talk",
        "Education Program",
        "Education Program talk",
        "TimedText",
        "TimedText talk",
        "Module",
        "Module talk",
        "Image"
    ]

    @classmethod
    def tag_to_surface(cls, re_tag_match):
        name = re_tag_match.group(1)
        body = re_tag_match.group(3)

        if name in ["div", "span", "sub", "sup"]:
            return body
        elif name == "code":
            if len(body) <= 16:
                return body
            else:
                return "code"
        elif name == "math":
            return "math"
        else:
            return ""

    @classmethod
    def bracket_to_surface(cls, re_bracket_match):
        items = re_bracket_match.group(1).split("|")
        top = items[0]

        if top == "仮リンク":
            return items[-1]
        elif top in ["IPA", "unicode", "lang"]:
            return items[-1]
        else:
            return ""

    @classmethod
    def link_to_surface(cls, re_link_match):
        entities = re_link_match.group(1).split("|")

        if len(entities) == 1:
            entity = entities[0]
            if entity.startswith("Category:"):
                return ""
            else:
                return entity
        elif len(entities) == 2:
            e0, e1 = entities
            if e0.startswith("File:"):
                return "File"
            else:
                return e1
        else:
            return ""

    @classmethod
    def document_to_sentences(cls, document):
        re_eos = re.compile(r"([.?!])\s+", re.DOTALL)

        sentences = []

        while True:
            match = re.search(re_eos, document)

            if match is None:
                if len(document) > 0:
                    sentences.append(document.strip("\n"))
                break

            sentence = document[:match.end(1)]
            sentences.append(sentence)
            document = document[match.end():]

        return sentences
