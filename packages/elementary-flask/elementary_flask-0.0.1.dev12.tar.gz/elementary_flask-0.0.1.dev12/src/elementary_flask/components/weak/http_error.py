__all__ = ['DefaultHTTPErrorRenderer', 'HTTPError']
from markupsafe import Markup

from elementary_flask.typing import RenderReturnValue
from .. import AbstractWeakComponent, AbstractRenderer


class DefaultHTTPErrorRenderer(AbstractRenderer):
    def render(self, weak_component: "HTTPError", **options) -> RenderReturnValue:
        return Markup('<h1 class="text-danger">') \
               + str(weak_component.status_code) + ' ' + weak_component.status_code_name + ': ' \
               + Markup('<small>') + weak_component.status_code_description + Markup('</small></h1>')


class HTTPError(AbstractWeakComponent):
    default_renderer = DefaultHTTPErrorRenderer()

    def __init__(self, status_code=500, status_code_name="Error", status_code_description=""):
        super(HTTPError, self).__init__()
        self.status_code = status_code
        self.status_code_name = status_code_name
        self.status_code_description = status_code_description
