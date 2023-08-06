# Copyright (c) 2021 T.Furukawa
# This software is released under the MIT License, see LICENSE.

from .language_base import *


class Japanese(LanguageBase):

    exclusive_title = [
        "メディア",
        "特別",
        "ノート",
        "利用者",
        "利用者‐会話",
        "Wikipedia",
        "Wikipedia‐ノート",
        "ファイル",
        "ファイル‐ノート",
        "MediaWiki",
        "MediaWiki‐ノート",
        "Template",
        "Template‐ノート",
        "Help",
        "Help‐ノート",
        "Category",
        "Category‐ノート",
        "Portal",
        "Portal‐ノート",
        "プロジェクト",
        "プロジェクト‐ノート",
        "モジュール",
        "モジュール‐ノート",
        "Gadget",
        "Gadget talk",
        "Gadget definition",
        "Gadget definition talk",
        "Topic",
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
                return "コード"
        elif name == "math":
            return "数式"
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
            if e0.startswith("ファイル:") or e0.startswith("File:"):
                return "ファイル"
            else:
                return e1
        else:
            return ""

    @classmethod
    def link_to_title(cls, re_link_match):
        entities = re_link_match.group(1).split("|")

        if len(entities) == 1:
            return entities[0]
        elif len(entities) == 2:
            e0, e1 = entities
            if e0.startswith("ファイル:") or e0.startswith("File:"):
                return None
            else:
                return e1
        else:
            return None

    @classmethod
    def document_to_sentences(cls, document):
        sentences = []

        while True:
            index = document.find("。")

            if index == -1:
                if len(document) > 0:
                    sentences.append(document.strip("\n"))
                break

            sentence = document[:index + 1]
            sentences.append(sentence.strip("\n"))
            document = document[index + 1:]

        return sentences
