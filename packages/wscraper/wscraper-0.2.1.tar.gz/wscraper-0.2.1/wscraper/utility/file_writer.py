# Copyright (c) 2021 T.Furukawa
# This software is released under the MIT License, see LICENSE.

from collections import OrderedDict


class FileWriter:

    def __init__(self, output_directory, path_format, threshold, *, prefix = None, suffix = None):
        self.output_directory = output_directory
        self.path_format = path_format
        self.threshold = threshold
        self.count = 0
        self.total_count = 0
        self.file_count = 0
        self.file_object = None
        self.prefix = prefix
        self.suffix = suffix

    def write(self, string, count = 1):
        if self.file_object is None:
            self.file_count += 1
            self.file_object = open(f"{self.output_directory}/{self.path_format.format(self.file_count)}", "w")
            if self.prefix is not None:
                self.file_object.write(self.prefix)

        self.file_object.write(string)
        self.count += count
        self.total_count += count

        if self.count >= self.threshold:
            if self.suffix is not None:
                self.file_object.write(self.suffix)
            self.file_object.close()
            self.file_object = None
            self.count = 0

    def finish(self):
        if self.file_object is not None:
            if self.suffix is not None:
                self.file_object.write(self.suffix)
            self.file_object.close()
            self.file_object = None

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, trace):
        self.finish()

    def for_progress_manager(self):
        return [{ "name": "writer", "value": self.total_count }, { "name": "page", "value": self.file_count }]
