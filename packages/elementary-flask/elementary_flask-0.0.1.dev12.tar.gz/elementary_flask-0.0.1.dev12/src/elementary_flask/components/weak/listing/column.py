__all__ = ['ListingColumn', 'listing_column']
from dataclasses import dataclass, field
from html import escape as html_escape

from elementary_flask.typing import Callable


@dataclass()
class ListingColumn:
    name: str
    title: str = None
    shrink_cell: bool = False
    td_class: str = None
    th_class: str = None
    safe_html: bool = False
    generator: Callable = None
    formatter: Callable = None
    order: int = 5
    _td_class: str = field(init=False, default=None)
    _th_class: str = field(init=False, default=None)

    def td(self, item):
        val = self.generator(item) if self.generator is not None else getattr(item, self.name, "None")
        val = str(val)
        if not self.safe_html:
            val = html_escape(val)
        if self.formatter:
            val = self.formatter(val)

        if self._td_class is None:
            _td_class = ((self.td_class or "") + " shrink-cell" if self.shrink_cell else "").strip()
            self._td_class = f'class="{_td_class} align-middle"' if _td_class else 'class="align-middle"'

        return f"""<td {self._td_class}>{val}</td>"""

    def th(self):
        if self.title is None:
            self.title = self.name
        if self._th_class is None:
            _th_class = ((self.th_class or "") + " shrink-cell" if self.shrink_cell else "").strip()
            self._th_class = f'class="{_th_class}"' if _th_class else ""
        return f"""<th {self._th_class} scope="col">{self.title}</th>"""


def listing_column(name, /, *,
                   title: str = None,
                   shrink_cell: bool = False,
                   td_class: str = None,
                   th_class: str = None,
                   safe_html: bool = False,
                   formatter: Callable = None,
                   order: int = 5):
    def decorator(f):
        return ListingColumn(name,
                             title=title,
                             shrink_cell=shrink_cell,
                             td_class=td_class,
                             th_class=th_class,
                             safe_html=safe_html,
                             formatter=formatter,
                             order=order,
                             generator=f)

    return decorator
