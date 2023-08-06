__all__ = ['ListingAction', 'listing_action', 'RedirectListingAction']

from dataclasses import dataclass

from markupsafe import Markup
from flask import url_for

from elementary_flask.typing import Callable, AbstractIcon, Union
from ... import get_icon
from elementary_flask.form import redirect


@dataclass()
class ListingAction:
    func: Callable
    name: str
    batch: bool = False
    form_cls: type = None
    hidden: bool = False
    title: str = None
    icon: Union[AbstractIcon, str] = None

    # TODO: button component

    def __post_init__(self):
        if self.icon and isinstance(self.icon, str):
            self.icon = get_icon(self.icon)

    def button_inner_html(self):
        if self.title and self.icon:
            return Markup(self.icon.render()) + " " + self.title
        if self.title:
            return self.title
        if self.icon:
            return Markup(self.icon.render())
        return self.name

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


class RedirectListingAction(ListingAction):
    def __init__(
            self,
            name: str, /, *,
            url: str = None,
            endpoint: str = None,
            endpoint_params: dict = None,
            hidden: bool = False,
            title: str = None,
            icon: Union[AbstractIcon, str] = None
    ):
        url = url or ''
        endpoint_params = endpoint_params or dict()

        def func(self, id_):
            if endpoint is not None:
                return redirect(url_for(endpoint, **{k: v.format(id_) for k, v in endpoint_params.items()}))
            return redirect(url.format(id_))

        super(RedirectListingAction, self).__init__(func=func, name=name, hidden=hidden, title=title, icon=icon)
        # self.url = url or ''
        # self.endpoint = endpoint
        # self.endpoint_params = endpoint_params or dict()

    # def __call__(self, *args, **kwargs):
    #     from elementary_flask.form import redirect
    #     from flask import url_for
    #     if self.endpoint is not None:
    #         return redirect(url_for(self.endpoint, **self.endpoint_params))
    #     return redirect(self.url)


def listing_action(name=None, /, *, batch=False, form_cls=None, hidden=False, icon=None, title=None):
    def decorator(f):
        n = name or f.__name__
        # f.elementary_flask_listing_action =
        return ListingAction(f, n, batch=batch, form_cls=form_cls, hidden=hidden, icon=icon, title=title)

    return decorator
