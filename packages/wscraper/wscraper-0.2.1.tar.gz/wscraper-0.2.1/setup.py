# Copyright (c) 2021 T.Furukawa
# This software is released under the MIT License, see LICENSE.

import os
from setuptools import setup, find_packages


def get_readme():
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md")) as f:
        return f.read()


setup(
    name = "wscraper",
    version = "0.2.1",
    license = "MIT License",
    author = "T.Furukawa",
    author_email = "tfurukawa.mail@gmail.com",
    url = "https://github.com/tfull/wikipedia_scraper",
    packages = find_packages(),
    keywords = ["Wikipedia"],
    description = "Scraping documents from a dump XML file of Wikipedia.",
    long_description = get_readme(),
    long_description_content_type = "text/markdown",
    entry_points = {
        "console_scripts": [
            "wscraper = wscraper.console:command"
        ]
    }
)
