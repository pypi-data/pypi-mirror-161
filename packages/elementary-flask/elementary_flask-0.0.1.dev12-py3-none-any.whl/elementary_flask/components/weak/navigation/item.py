__all__ = ['NavigationLink', 'NavigationItem', 'NavigationGroup', 'NavigationSeparator']

from dataclasses import dataclass
from html import escape as html_escape

from elementary_flask.globals import current_elementary_flask_app as _app
from elementary_flask.typing import Optional, AbstractIcon, List, Callable, Union


@dataclass
class NavigationItem:
    title: str
    icon: Optional[AbstractIcon] = None
    link: Optional[str] = None
    endpoint: Optional[Union[Callable, str]] = None
    params: Optional[dict] = None
    disabled: bool = False
    navigation_type: str = 'link'


class NavigationLink(NavigationItem):
    def __init__(self,
                 title: str,
                 icon: Optional[AbstractIcon] = None,
                 link: Optional[str] = None,
                 endpoint: Optional[Union[Callable, str]] = None,
                 params: Optional[dict] = None,
                 disabled: bool = False,
                 ):
        if not link and not endpoint:
            raise ValueError("link or endpoint should be set ")
        super(NavigationLink, self).__init__(title, navigation_type='link', icon=icon, link=link, endpoint=endpoint,
                                             params=params, disabled=disabled)

    def get_link(self):
        if self.link is None and self.endpoint is not None:
            params = self.params or dict()
            endpoint = self.endpoint() if callable(self.endpoint) else self.endpoint
            self.link = _app.url_for(endpoint, **params)

        return self.link

    def get_html_title(self):
        _title = html_escape(self.title)
        if self.icon:
            _title = self.icon.render() + ' ' + _title
        return _title


class NavigationGroup(NavigationItem):
    def __init__(self, title, icon=None, items_list: List[NavigationItem] = None):
        super(NavigationGroup, self).__init__(title, navigation_type='group', icon=icon)
        self.items_list = items_list or list()

    def __iter__(self):
        return self.items_list.__iter__()


class NavigationSeparator(NavigationItem):
    def __init__(self):
        super(NavigationSeparator, self).__init__(None, navigation_type='separator')
