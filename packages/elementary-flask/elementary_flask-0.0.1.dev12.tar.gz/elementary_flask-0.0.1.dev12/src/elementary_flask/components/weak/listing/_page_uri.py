__all__ = ['page_uri']
from urllib.parse import urlencode


def page_uri(*, page=None, filters=None, query=None, sort=None):
    t = list()
    for k, v in (("page", page), ('filters', filters), ('query', query), ('sort', sort)):
        if v and (k != 'page' or v != 1):
            t.append((k, v), )
    return '?' + urlencode(t)  # if t else '#'
