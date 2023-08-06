# Copyright (c) 2021 T.Furukawa
# This software is released under the MIT License, see LICENSE.

import re
import sys
import glob
import os

from ..utility import *
from .config import *
from .wscraper_exception import *


class Builder:

    @classmethod
    def command_import(cls, wikipedia_xml, wikipedia_name, *, move = False, copy = False, reset = False, language = None):
        Config.check_root_directory_exists()

        if not wikipedia_xml.endswith(".xml"):
            raise WScraperException("XML file required.")

        if move and copy:
            raise WScraperException("Both move and copy are True. Nothing or one should be True.")

        if wikipedia_name is None:
            wikipedia_name = os.path.basename(wikipedia_xml)[:-4]

        target_directory = os.path.join(Constant.wikipedia_directory, wikipedia_name)

        if os.path.isdir(target_directory):
            if not reset:
                sys.stdout.write("Split XML files are already exist. Skipping.\n")
                return
            else:
                sys.stdout.write("Split XML files are exist. Removing.\n")
                for path in glob.glob(os.path.join(target_directory, "*.xml")):
                    os.remove(path)
        else:
            os.makedirs(target_directory)

        sys.stdout.write(f"Split Wikipedia XML file `{wikipedia_xml}` to `{target_directory}`.\n")
        cls.split_to_xmls(wikipedia_xml, target_directory, chunk = Config.load_root_config()["page_chunk"])
        sys.stdout.write("Done!\n")

        if copy:
            sys.stdout.write(f"File is copying.\n")
            new_path = shutil.copy(wikipedia_xml, target_directory + ".xml")
            sys.stdout.write(f"File was copied to {new_path}.\n")
        elif move:
            new_path = shutil.move(wikipedia_xml, target_directory + ".xml")
            sys.stdout.write(f"File was moved {wikipedia_xml} to {new_path}.\n")

        Config.create_config(wikipedia_name, exist_ok = True)
        if language is not None:
            config = Config(wikipedia_name)
            config.set_language(language)
            config.save()
            sys.stdout.write(f"Language {language} is set to {wikipedia_name}.\n")

    @classmethod
    def split_to_xmls(cls, xml_path, output_directory, *, chunk = 10000):
        if not (type(chunk) == int and chunk >= Constant.min_page_chunk and chunk <= Constant.max_page_chunk):
            raise WScraperException("Config page_chunk must satisfy 100 <= chunk <= 10 ** 7.")

        re_start = re.compile(r"<page>")
        re_end = re.compile(r"</page>")

        flag = False
        body = []

        reader = open(xml_path, "r")
        writer = FileWriter(output_directory, "{:04d}.xml", chunk, prefix = "<wikipedia>\n", suffix = "</wikipedia>\n")

        progress = ProgressManager(writer)

        with reader, writer, progress:
            for line in reader:
                progress.update()

                if re_start.search(line):
                    flag = True

                if flag:
                    body.append(line)

                if re_end.search(line):
                    flag = False
                    writer.write("".join(body), count = 1)
                    body = []
