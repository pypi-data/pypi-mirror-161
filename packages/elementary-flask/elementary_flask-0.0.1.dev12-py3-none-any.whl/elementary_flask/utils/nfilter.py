__all__ = ['NFilter', 'nfilter']

from elementary_flask.typing import Optional, Callable, Iterable


class NFilter:
    def __init__(self, func, iterable):
        self.filters = []
        self.append_filter(func)
        self.iterable = iterable

    def append_filter(self, func):
        if func:
            self.filters.append(func)

    def __iter__(self):
        return filter(
            lambda itm: all(f(itm) for f in self.filters),
            self.iterable
        )


def nfilter(func: Optional[Callable], iterable: Iterable):
    if not isinstance(iterable, NFilter):
        return NFilter(func, iterable)
    else:
        iterable.append_filter(func)
        return iterable
