# Copyright (c) 2021 T.Furukawa
# This software is released under the MIT License, see LICENSE.

import sys
import time


class ProgressManager:

    class Console:
        def __init__(self):
            self.last = -1

        def output(self, string, *, force = False):
            now = time.time()

            if force or now - self.last >= 1 / 60:
                self.last = now
                sys.stderr.write(string)
                sys.stderr.flush()

    class Notebook:
        def __init__(self):
            self.last = -1

        def output(self, string, *, force = False):
            now = time.time()

            if force or now - self.last >= 1:
                self.last = now
                import IPython.display as ds
                ds.clear_output()
                sys.stderr.write(string)
                sys.stderr.flush()

    def __init__(self, * instances):
        if "ipykernel" in sys.modules:
            self.output_type = self.Notebook()
        else:
            self.output_type = self.Console()

        self.instances = list(instances)
        self.count = 0

    def get_globals(self):
        return globals()

    def add(self, instance):
        self.instances.append(instance)

    def add_list(self, instances):
        self.instances.extend(instances)

    def add_count(self):
        self.count += 1

    def start(self):
        self.time = time.time()

    def finish(self):
        self.update(count_up = False, force = True, newline = True)

    def update(self, *, count_up = True, force = False, newline = False):
        now = time.time()

        interval = int(now - self.time)

        if count_up:
            self.add_count()

        second = interval % 60
        minute = interval % 3600 // 60
        hour = interval // 3600

        output_time = f"{hour}:{minute:02d}:{second:02d}"
        output_count = f"{self.count} count"

        output_base = f"\033[2K\033[G[progress] ({output_time}, {output_count})"

        if len(output_base) == 0:
            output_result = output_base
        else:
            output_others = [f"{x['name']}: {x['value']}" for inst in self.instances for x in inst.for_progress_manager()]
            output_result = f"{output_base}, {', '.join(output_others)}"

        if newline:
            output_result += "\n"

        self.output_type.output(output_result, force = force)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, ex_type, ex_value, trace):
        self.finish()
