# Copyright (c) 2021 T.Furukawa
# This software is released under the MIT License, see LICENSE.


import re
import os
import sys
import shutil
import glob

from .constant import *
from .wscraper_exception import *
from ..utility import *


class WScraperConfigError(WScraperException):
    pass


class Config:

    template_root_config = {
        "language": None,
        "page_chunk": 10000
    }

    template_config = {
        "language": None
    }

    template_root_status = {
        "current": None
    }

    @classmethod
    def check_name_format(cls, name):
        return re.search(Constant.name_format, name) is not None

    @classmethod
    def check_root_directory_exists(cls):
        if not os.path.isdir(Constant.root_directory):
            message = f"Root directory {Constant.root_directory} does not exist."
            message += " Did you run `wscraper initialize`?"
            raise WScraperConfigError(message)

        if not os.path.isfile(Constant.root_config):
            raise WScraperConfigError(f"Root config file {Constant.root_config} does not exist.")

        if not os.path.isfile(Constant.root_status):
            raise WScraperConfigError(f"Root status file {Constant.root_status} does not exist.")

        if not os.path.isdir(Constant.wikipedia_directory):
            raise WScraperConfigError(f"Wikipedia directory {Constant.wikipedia_directory} does not exist.")

    @classmethod
    def command_root_status(cls):
        cls.check_root_directory_exists()

        config = cls.load_root_config()
        sys.stdout.write("\nRoot Status\n\n")
        sys.stdout.write(f"language: {config['language'] or '[not set]'}\n")
        sys.stdout.write(f"page_chunk: {config['page_chunk']}\n")
        sys.stdout.write("\n")

    @classmethod
    def command_root_set(cls, language, page_chunk):
        cls.check_root_directory_exists()

        config = cls.load_root_config()

        if language is not None:
            if language not in Constant.available_languages:
                raise WScraperConfigError(f"language `{language}` is not supported.")

            config["language"] = language

        if page_chunk is not None:
            if not (page_chunk >= Constant.min_page_chunk and page_chunk <= Constant.max_page_chunk):
                raise WScraperConfigError(f"page_chunk should satisfy {Constant.min_page_chunk} <= page_chunk <= {Constant.max_page_chunk}.")

            config["page_chunk"] = page_chunk

        FileManager.save_json(Constant.root_config, config)

    @classmethod
    def command_root_unset(cls, language):
        cls.check_root_directory_exists()

        config = cls.load_root_config()

        if language:
            config["language"] = None

        FileManager.save_json(Constant.root_config, config)

    @classmethod
    def command_initialize(cls):
        if os.path.isdir(Constant.root_directory):
            sys.stdout.write(f"Root directory {Constant.root_directory} already exists.\n")

            if os.path.isfile(Constant.root_config):
                sys.stdout.write(f"Root config {Constant.root_config} already exists.\n")
            else:
                FileManager.save_json(Constant.root_config, cls.template_root_config)
                sys.stdout.write(f"Root config {Constant.root_config} was created.\n")

            if os.path.isfile(Constant.root_status):
                sys.stdout.write(f"Root status {Constant.root_status} already exists.\n")
            else:
                FileManager.save_json(Constant.root_status, cls.template_root_status)
                sys.stdout.write(f"Root status {Constant.root_status} was created.\n")

            if os.path.isdir(Constant.wikipedia_directory):
                sys.stdout.write(f"Wikipedia directory {Constant.wikipedia_directory} already exists.\n")
            else:
                os.makedirs(Constant.wikipedia_directory)
                sys.stdout.write(f"Wikipedia directory {Constant.wikipedia_directory} was created.\n")

        else:
            os.makedirs(Constant.root_directory)
            sys.stdout.write(f"Root directory {Constant.root_directory} was created.\n")
            FileManager.save_json(Constant.root_config, cls.template_root_config)
            sys.stdout.write(f"Root config {Constant.root_config} was creaetd.\n")
            FileManager.save_json(Constant.root_status, cls.template_root_status)
            sys.stdout.write(f"Root status {Constant.root_status} was created.\n")
            os.makedirs(Constant.wikipedia_directory)
            sys.stdout.write(f"Wikipedia directory {Constant.wikipedia_directory} was created.\n")

    @classmethod
    def command_switch(cls, name):
        cls.check_root_directory_exists()

        if not os.path.isdir(os.path.join(Constant.wikipedia_directory, name)):
            raise WScraperConfigError(f"Wikipedia name {name} does not exist.")

        path = os.path.join(Constant.root_directory, "status.json")
        status = FileManager.load_json(path)
        status["current"] = name
        FileManager.save_json(path, status)
        sys.stdout.write(f"Wikipedia switched to {name}.\n")

    @classmethod
    def command_set(cls, language):
        cls.check_root_directory_exists()

        config = Config()

        if language is not None:
            config.set_language(language)

        config.save()

    @classmethod
    def command_unset(cls, language):
        cls.check_root_directory_exists()

        config = Config()

        if language:
            config.unset_language()

        config.save()

    @classmethod
    def command_status(cls):
        cls.check_root_directory_exists()

        Config().print_status()

    @classmethod
    def command_rename(cls, source, target):
        cls.check_root_directory_exists()

        if not cls.check_name_format(target):
            raise WScraperConfigError(f"illegal name format: \"{target}\"")

        s = os.path.join(Constant.wikipedia_directory, source)
        sc = os.path.join(Constant.wikipedia_directory, f"{source}.config.json")
        sx = os.path.join(Constant.wikipedia_directory, f"{source}.xml")

        if not os.path.isdir(s) or not os.path.isfile(sc):
            raise WScraperConfigError(f"no such wikipedia corpus: \"{source}\"")

        t = os.path.join(Constant.wikipedia_directory, target)
        tc = os.path.join(Constant.wikipedia_directory, f"{target}.config.json")
        tx = os.path.join(Constant.wikipedia_directory, f"{target}.xml")

        if os.path.exists(t) or os.path.exists(tc):
            raise WScraperConfigError(f"Wikipedia corpus {target} already exists.")

        shutil.move(s, t)
        shutil.move(sc, tc)

        if os.path.isfile(sx):
            shutil.move(sx, tx)

        sys.stdout.write(f"rename: {source} -> {target}\n")

    @classmethod
    def command_delete(cls, target):
        cls.check_root_directory_exists()

        t = os.path.join(Constant.wikipedia_directory, target)
        tc = os.path.join(Constant.wikipedia_directory, f"{target}.config.json")
        tx = os.path.join(Constant.wikipedia_directory, f"{target}.xml")

        if os.path.isdir(t) and os.path.isfile(tc):
            shutil.rmtree(t)
            os.remove(tc)
            if os.path.isfile(tx):
                os.remove(tx)
            sys.stdout.write(f"delete: {target}\n")
        else:
            raise WScraperConfigError(f"no such wikipedia corpus: \"{target}\"")

    @classmethod
    def command_list(cls):
        sys.stdout.write("\n")

        list_wikipedia = cls.list_wikipedia()

        if len(list_wikipedia) == 0:
            sys.stdout.write("Available Wikipedia is nothing.\n")
        else:
            sys.stdout.write("Available Wikipedia:\n")
            for item in list_wikipedia:
                sys.stdout.write(f"  - {item}\n")

        sys.stdout.write("\n")

    @classmethod
    def list_wikipedia(cls):
        items = []

        for path in glob.glob(os.path.join(Constant.wikipedia_directory, "*")):
            if os.path.isdir(path):
                items.append(os.path.basename(path))

        return items

    @classmethod
    def load_root_config(cls):
        return FileManager.load_json(Constant.root_config)

    @classmethod
    def load_root_status(cls):
        return FileManager.load_json(Constant.root_status)

    @classmethod
    def load_config_by_name(cls, name):
        path = os.path.join(Constant.wikipedia_directory, f"{name}.config.json")

        if not os.path.isfile(path):
            raise WScraperConfigError(f"Wikipedia name {name} does not exist.")

        return FileManager.load_json(path)

    @classmethod
    def validate_name(cls, name):
        if re.search(Constant.name_format, name) is None:
            raise WScraperConfigError(f"invalid name `{name}`.")

    @classmethod
    def create_config(cls, name, *, exist_ok = False):
        path = os.path.join(Constant.wikipedia_directory, f"{name}.config.json")

        if os.path.isfile(path):
            if not exist_ok:
                raise WScraperConfigError(f"Wikipedia name {name} already exists.")
        else:
            cls.validate_name(name)
            FileManager.save_json(path, cls.template_config)

    def __init__(self, name = None):
        self.check_root_directory_exists()

        if name is None:
            status = FileManager.load_json(Constant.root_status)
            name = status["current"]
            if name is None:
                raise WScraperConfigError("Current name is not set.")

        self.name = name
        self.config = self.load_config_by_name(name)
        self.root_config = self.load_root_config()
        self.root_status = self.load_root_status()
        self.path = os.path.join(Constant.wikipedia_directory, f"{self.name}.config.json")

    def save(self):
        FileManager.save_json(self.path, self.config)

    def print_status(self):
        print("\ncurrent:", self.name)

        print()

        language = self.config["language"]

        if language is None:
            print("language [defalt]:", self.root_config["language"] or "[not set]")
        else:
            print("language:", language)

        print()

    def get_parameter(self, key, *, must = False):
        data = self.config

        for k in key.split("."):
            if data is not None:
                data = data.get(k)

        if data is None and key in self.template_root_config:
            data = self.root_config[key]

        if data is None and must:
            raise WScraperConfigError(f"Key {key} must exist but None.")

        return data

    def set_language(self, language):
        if language not in Constant.available_languages:
            raise WScraperConfigError(f"Language `{language}` is not supported.")

        self.config["language"] = language
        self.save()

    def unset_language(self):
        self.config["language"] = None
        self.save()

    def get_language(self, must = False):
        return self.get_parameter("language", must = must)

    def get_wikipedia_xml(self, *, must = True):
        wikipedia_xml = os.path.join(Constant.wikipedia_directory + f"{self.name}.xml")

        if must and not os.path.isfile(wikipedia_xml):
            raise WScraperConfigError(f"No such file {wikipedia_xml}.")

        return wikipedia_xml

    def get_wikipedia_xml_directory(self, *, must = True):
        return os.path.join(Constant.wikipedia_directory, f"{self.name}")
