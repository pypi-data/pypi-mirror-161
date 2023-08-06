import collections.abc as collections_abc
from pathlib import Path
from typing import Iterable


def chain_func(start, *funcs):
    res = start
    for func in funcs:
        res = func(res)
    return res


def listify(x) -> list:
    """Ensure list type. Create a copy."""
    if isinstance(x, (str, bytes)):
        return [x]
    try:
        return [_ for _ in x]
    except TypeError:
        return [x]


class ChangingListIterator(collections_abc.Iterator):
    def __init__(self, iterable):
        self.iterable = iterable
        self.current_element = None
        self.current_index = 0

    def __iter__(self):
        self.current_element = None
        self.current_index = 0
        return self

    def __next__(self):
        try:
            if self.current_index == 0 and self.current_element is None:
                self.current_element = self.iterable[self.current_index]
                return self.current_element

            check_element = self.iterable[self.current_index]
            if self.current_element is check_element:
                self.current_index += 1
            self.current_element = self.iterable[self.current_index]
        except IndexError:
            raise StopIteration
        return self.current_element

    def enumerate(self):
        return EnumeratedChangingListIterator(self.iterable)


class EnumeratedChangingListIterator(ChangingListIterator):
    def __next__(self):
        super().__next__()
        return self.current_index, self.current_element


def read_file(p: Path | str) -> str:
    with open(p) as file:
        content = file.read()
    return content
