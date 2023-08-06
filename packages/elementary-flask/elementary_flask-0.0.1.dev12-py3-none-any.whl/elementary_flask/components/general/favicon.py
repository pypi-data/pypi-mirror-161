__all__ = ['FavIcon']
from dataclasses import dataclass, field
from html import escape as html_escape


@dataclass
class FavIcon:
    href: str
    rel: str = "icon"
    mimetype: str = "image/x-icon"
    rendered: str = field(init=False, repr=False)

    def __post_init__(self):
        self.rendered = f'<link rel="{self.rel}" type="{self.mimetype}" href="{html_escape(self.href)}">'
