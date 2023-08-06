__all__ = ['AbstractPageLayout', 'EmptyPageLayout', 'LayoutMapping']

from abc import ABC

from elementary_flask.globals import current_elementary_flask_app as _app
from elementary_flask.typing import Tuple, Optional, RenderReturnValue
from .page import AbstractPage
from .page_response import PageResponse
from .. import render


# class BlockNotRenderable(Exception):
#     pass


class AbstractPageLayout(AbstractPage, ABC):
    block_names: Tuple[str] = ('main',)

    def render_page_content(self, page_response, **options) -> RenderReturnValue:
        return self.render_layout(page_response, **options)

    def render_layout(self, page_response: PageResponse, **options) -> RenderReturnValue:
        raise NotImplementedError()


class EmptyPageLayout(AbstractPageLayout):
    def render_layout(self, page_response: PageResponse, **options) -> RenderReturnValue:
        return render(page_response.blocks.get('main', None))


class LayoutMapping:
    def __init__(self, parent: Optional["LayoutMapping"] = None, **layouts):
        self.parent = parent
        self.layouts = layouts

    def get_layout(self, layout):
        ret = self._get_layout(layout, [])
        if ret:
            return ret
        return self._get_layout('default', [])

    def _get_layout(self, layout, ignore):
        if layout in self.layouts:
            return self.layouts[layout]

        if self.parent is None and self != _app.layout_mapping:
            self.parent = _app.layout_mapping

        if self.parent and self.parent not in ignore:
            ignore.append(layout)
            return self.parent._get_layout(layout, ignore)

        return None
        # return _app.get_layout(layout, ignore)
