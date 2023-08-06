__all__ = ['get_parsed_sort', 'dump_sort']

from flask import request, g

SORT_GLOBAL_KEY = 'elementary_flask_listing_parsed_sort'


def get_parsed_sort(default_sort=None):
    if not hasattr(g, SORT_GLOBAL_KEY):
        ret = list()
        sort = request.args.get('sort', None) or default_sort
        if sort:
            # ret = json.loads('{' + filters + '}')
            for s in sort.split(';'):  # TODO: character escaping??
                if ':' in s:
                    ss = s.split(':')
                    k, o = ss[0], _normalize_sort_direction(ss[1])

                else:
                    k = s
                    o = 'asc'
                ret.append((k, o))
        setattr(g, SORT_GLOBAL_KEY, ret)
    return getattr(g, SORT_GLOBAL_KEY)


def _normalize_sort_direction(o):
    o = o.lower()
    if o not in ('desc', 'asc'):
        return 'asc'
    return o


def dump_sort(sort=None):
    if sort:
        # return json.dumps(filters)[1: -1]
        return ";".join(f'{k}:{_normalize_sort_direction(o)}' for k, o in sort)
    return None
