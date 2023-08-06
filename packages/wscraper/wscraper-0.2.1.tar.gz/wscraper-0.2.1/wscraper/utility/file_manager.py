# Copyright (c) 2021 T.Furukawa
# This software is released under the MIT License, see LICENSE.

import json
import xml.etree.ElementTree


class FileManager:

    @classmethod
    def load_xml(cls, path):
        with open(path, "r") as f:
            parser = xml.etree.ElementTree.XMLParser()

            for line in f:
                parser.feed(line)

            return parser.close()

    @classmethod
    def load_json(cls, path):
        with open(path, "r") as f:
            return json.load(f)

    @classmethod
    def save_json(cls, path, data):
        with open(path, "w") as f:
            json.dump(data, f, indent = 2)
            f.write("\n")
