__all__ = ['ListingFilter', 'listing_filter', 'get_parsed_filters', 'TRUE_FALSE_TOGGLE']

from collections.abc import Iterable
from dataclasses import dataclass, field

from flask import g, request
from markupsafe import Markup

from elementary_flask.globals import current_elementary_flask_app as _app
from elementary_flask.typing import Union, Callable, Tuple, AbstractIcon
from ._page_uri import page_uri
from ... import get_icon

FILTERS_GLOBAL_KEY = 'elementary_flask_listing_parsed_filters'


class TrueFalseChoices:
    choices = (("true", "true"), ("false", "false"))


TRUE_FALSE_TOGGLE = TrueFalseChoices()


def get_parsed_filters():
    if not hasattr(g, FILTERS_GLOBAL_KEY):
        ret = dict()
        filters = request.args.get('filters', None) or None
        if filters:
            # ret = json.loads('{' + filters + '}')
            for s in filters.split(';'):  # TODO: character escaping??
                try:
                    # ret.append(s.split('='))
                    k, v = s.split('=')
                    ret[k] = v
                except ValueError:
                    _app.logger.warning("ignored bad filter value: %s", s)
        setattr(g, FILTERS_GLOBAL_KEY, ret)
    return getattr(g, FILTERS_GLOBAL_KEY)


def dump_filters(filters=None):
    if filters:
        # return json.dumps(filters)[1: -1]
        return ";".join(f'{k}={v}' for k, v in filters.items())
    return None


@dataclass
class ListingFilter:
    name: str
    choices: Union[TrueFalseChoices, Iterable[str], Iterable[Tuple[str, str]], Callable] = TRUE_FALSE_TOGGLE
    icon: AbstractIcon = None
    title: str = None
    check_icon: AbstractIcon = None
    order: int = 5
    append_to_search: bool = False
    toggle: bool = field(init=False, default=False)
    callable: bool = field(init=False, default=False)

    def __post_init__(self):
        if isinstance(self.choices, TrueFalseChoices):
            self.choices = self.choices.choices
            self.toggle = True
        elif isinstance(self.choices, Iterable):
            self.choices = self._process_choices_iterable(self.choices)
        elif callable(self.choices):
            self.callable = True
        else:
            raise ValueError("Unsupported choice format: %s", self.choices)

        if not self.title:
            self.title = self.name
        # self.title = escape(self.title)

        if isinstance(self.icon, str):
            self.icon = get_icon(self.icon)

        if self.icon:
            self.title = Markup(self.icon.render()) + ' ' + self.title

    @staticmethod
    def _process_choices_iterable(choices: Iterable):
        if choices is None:
            return tuple()
        chs = list()
        for c in choices:
            if isinstance(c, tuple) and len(c) == 2:
                chs.append(c)
            elif isinstance(c, str):
                chs.append((c, c))
            else:
                raise ValueError("Unsupported choice format: %s", c)
        return tuple(chs)

    def active(self, choice=None):
        if choice is None:
            return self.name in get_parsed_filters()
        return get_parsed_filters().get(self.name, None) == choice

    def __call__(self, *args, **kwargs):
        if self.callable:
            choices = self._process_choices_iterable(self.choices(*args, **kwargs))  # noqa
        else:
            choices = self.choices
        if not choices and self.name in get_parsed_filters():
            return (get_parsed_filters()[self.name], get_parsed_filters()[self.name]),
        return choices

    def choice_link(self, choice):
        new_filters = dict(get_parsed_filters())
        if new_filters.get(self.name, None) == choice:
            del new_filters[self.name]
        else:
            new_filters[self.name] = choice
        return page_uri(query=request.args.get('query', None), filters=dump_filters(new_filters),
                        sort=request.args.get('sort', None))


def listing_filter(name, /, *,
                   icon: AbstractIcon = None,
                   title: str = None,
                   check_icon: AbstractIcon = None,
                   order: int = 5,
                   append_to_search: bool = False,
                   ):
    def decorator(f):
        return ListingFilter(name,
                             title=title,
                             icon=icon,
                             check_icon=check_icon,
                             append_to_search=append_to_search,
                             order=order,
                             choices=f)

    return decorator
