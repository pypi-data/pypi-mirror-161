# Copyright (c) 2021 T.Furukawa
# This software is released under the MIT License, see LICENSE.


class CombinedIterator:

    def __init__(self, *iterators):
        self.iterators = list(iterators)
        self.n_iterator = len(iterators)

    def __iter__(self):
        self.i_iterator = 0

        for i in range(self.n_iterator):
            self.iterators[i] = iter(self.iterators[i])

        return self

    def __next__(self):

        while True:
            if self.i_iterator >= self.n_iterator:
                raise StopIteration()

            try:
                return next(self.iterators[self.i_iterator])
            except StopIteration:
                self.i_iterator += 1
