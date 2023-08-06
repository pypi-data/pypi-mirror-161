# Copyright (c) 2021 T.Furukawa
# This software is released under the MIT License, see LICENSE.

import sys
import argparse

from .base import *


help_string = """
wscraper

Wikipedia Scraper
    language model using Wikipedia

Command:
    wscraper initialize
        make root directory of wscraper and config file
    wscraper status
        describe status of current wikipedia corpus
    wscraper switch [name]
        change current wikipedia corpus to [name]
    wscraper import [xml path] [options...]
        read [xml path] and locate wikipedia resource directory
    wscraper set [parameters...]
        set parameters for current wikipedia corpus
    wscraper unset [parameters...]
        unset parameters for current wikipedia corpus
    wscraper rename [source] [target]
        rename wikipedia corpus from [source] to [target]
    wscraper root status
        check root configuration
    wscraper root set [parameters...]
        set root parameters
    wscraper root unset [parameters...]
        unset root parameters
    wscraper list
        list up names of wikipedia corpus resources
"""


def command():
    map_command_function = {
        "initialize": command_initialize,
        "status": command_status,
        "switch": command_switch,
        "import": command_import,
        "set": command_set,
        "unset": command_unset,
        "rename": command_rename,
        "delete": command_delete,
        "root": command_root,
        "list": command_list
    }

    if len(sys.argv) < 2 or sys.argv[1] in ["help", "-h", "--help"]:
        sys.stderr.write(f"{help_string}\n")
        sys.exit(1)

    command = sys.argv[1]

    if command not in map_command_function:
        sys.stderr.write(f"{help_string}\n")
        sys.exit(1)

    map_command_function[command](sys.argv[2:])


def command_initialize(args):
    parser = argparse.ArgumentParser(
        prog = "wscraper initialize",
        description = "Command `wscraper initialize` creates primary files and directories."
    )

    args = parser.parse_args(args)

    Config.command_initialize()


def command_import(args):
    parser = argparse.ArgumentParser(
        prog = "wscraper import",
        description = "Command `wscraper import` move a wikipedia.xml file to wscraper directory and split one to small files."
    )

    parser.add_argument("source", help = "source wikipedia.xml file")
    parser.add_argument("-n", "--name", help = "target directory name")
    parser.add_argument("-l", "--language", help = "language of wikipedia file")
    parser.add_argument("-m", "--move", action = "store_true", help = "move file to wscraper directory for backup")
    parser.add_argument("-c", "--copy", action = "store_true", help = "copy file to wscraper directory for backup")
    parser.add_argument("-r", "--reset", action = "store_true", help = "remove existing file")

    args = parser.parse_args(args)

    Builder.command_import(
        args.source, args.name,
        move = args.move, copy = args.copy, reset = args.reset, language = args.language
    )


def command_switch(args):
    parser = argparse.ArgumentParser(
        prog = "wscraper switch",
        description = "Command `wscraper switch` switches the current wikipedia corpus."
    )

    parser.add_argument("name", help = "wikipedia name")

    args = parser.parse_args(args)

    Config.command_switch(args.name)


def command_rename(args):
    parser = argparse.ArgumentParser(
        prog = "wscraper rename",
        description = "Command `wscraper rename` changes a name of wikipedia corpus."
    )

    parser.add_argument("source", help = "name from")
    parser.add_argument("target", help = "name to")

    args = parser.parse_args(args)

    Config.command_rename(args.source, args.target)


def command_delete(args):
    parser = argparse.ArgumentParser(
        prog = "wscraper delete",
        description = "Command `wscraper delete` removes the wikipedia corpus."
    )

    parser.add_argument("target", help = "remove")

    args = parser.parse_args(args)

    Config.command_delete(args.target)


def command_status(args):
    parser = argparse.ArgumentParser(
        prog = "wscraper status",
        description = "Command `wscraper status` shows a status of current wikipedia."
    )

    try:
        Config.command_status()
    except WScraperConfigError:
        sys.stderr.write("no wikipedia is set\n")
        sys.exit(1)


def command_set(args):
    parser = argparse.ArgumentParser(
        prog = "wscraper set",
        description = "Command `wscraper set` sets value of parameter."
    )

    parser.add_argument("--language", help = "Wikipedia language")

    args = parser.parse_args(args)

    try:
        Config.command_set(language = args.language)
    except WScraperConfigError as e:
        sys.stderr.write(f"{e}\n")
        sys.exit(1)


def command_unset(args):
    parser = argparse.ArgumentParser(
        prog = "wscraper unset",
        description = "Command `wscraper unset` unsets value of parameter."
    )

    parser.add_argument("--language", action = "store_true", help = "Wikipedia language")

    args = parser.parse_args(args)

    try:
        Config.command_unset(language = args.language)
    except WScraperConfigError as e:
        sys.stderr.write(f"{e}\n")
        sys.exit(1)


def command_list(args):
    parser = argparse.ArgumentParser(
        prog = "wscraper list",
        description = "Command `wscraper list` shows available wikipedia names."
    )

    Config.command_list()


def command_root(args):
    if len(args) == 0:
        sys.stderr.write("Command `wscraper root` requires at least 1 argument.\n")
        sys.exit(1)

    sub_command = args[0]

    if sub_command == "status":
        Config.command_root_status()
    elif sub_command == "set":
        command_root_set(args[1:])
    elif sub_command == "unset":
        command_root_unset(args[1:])
    else:
        sys.stderr.write("Command `wscraper root` requires following string as a first argument. {status, set, unset}\n")
        sys.exit(1)


def command_root_set(args):
    parser = argparse.ArgumentParser(
        prog = "wscraper root set",
        description = "Command `wscraper root set` sets default values of parameters."
    )

    parser.add_argument("--language", help = "language of wikipedia corpus")
    parser.add_argument("--page_chunk", type = int, help = "a unit of partition")

    args = parser.parse_args(args)

    Config.command_root_set(args.language, args.page_chunk)


def command_root_unset(args):
    parser = argparse.ArgumentParser(
        prog = "wscraper root unset",
        description = "Command `wscraper root unset` unsets default values of parameters."
    )

    parser.add_argument("--language", action = "store_true", help = "language of wikipedia corpus")

    args = parser.parse_args(args)

    Config.command_root_unset(args.language)
