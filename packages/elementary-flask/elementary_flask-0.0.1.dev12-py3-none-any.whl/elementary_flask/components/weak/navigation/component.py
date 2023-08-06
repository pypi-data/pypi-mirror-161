__all__ = ['Navigation', 'default_navigation_renderer']
from abc import ABC

from elementary_flask.typing import RenderReturnValue
from .item import NavigationLink
from .provider import AbstractNavigationProvider, DefaultNavigationProvider
from ... import AbstractWeakComponent

_default_provider = DefaultNavigationProvider()


def default_navigation_renderer(navigation: "Navigation") -> RenderReturnValue:
    ret = '<ul>'
    for itm in navigation.navigation_provider.generate_navigation():
        if isinstance(itm, NavigationLink):
            ret += f"""<li class="nav-item"><a class="nav-link" href="{itm.get_link()}">{itm.get_html_title()}</a></li>"""
    ret += '</ul>'
    return ret


class Navigation(AbstractWeakComponent, ABC):
    default_renderer = default_navigation_renderer

    def __init__(self, navigation_provider: AbstractNavigationProvider = None):
        super().__init__()
        self.navigation_provider = navigation_provider or _default_provider
