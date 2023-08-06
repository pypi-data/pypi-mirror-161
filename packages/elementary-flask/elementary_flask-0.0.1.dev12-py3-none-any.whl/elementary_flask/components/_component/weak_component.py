__all__ = ['AbstractRenderer', 'AbstractWeakComponent', 'find_renderer']

from abc import ABC, abstractmethod

from elementary_flask.globals import current_elementary_flask_app as _app
from elementary_flask.typing import RenderReturnValue, Renderer, Optional
from .component import AbstractComponent


class AbstractRenderer(AbstractComponent, ABC):
    @abstractmethod
    def render(self, weak_component: "AbstractWeakComponent", /, **options) -> RenderReturnValue:
        raise NotImplementedError()

    def __call__(self, weak_component: "AbstractWeakComponent", /, **options) -> RenderReturnValue:
        return self.render(weak_component, **options)


def repr_render(weak_component: "AbstractWeakComponent", /, **options) -> RenderReturnValue:
    return repr(weak_component)


class AbstractWeakComponent(AbstractComponent):
    default_renderer: Renderer = repr_render
    _renderer: Renderer = None

    def render(self, **options) -> RenderReturnValue:
        return self.find_renderer()(self, **options)

    @staticmethod
    def get_renderer() -> Optional[Renderer]:
        return None

    @classmethod
    def find_renderer(cls) -> Renderer:
        cls._renderer = cls._renderer or find_renderer(cls) or cls.get_renderer() or cls.default_renderer
        if cls._renderer is None:
            raise Exception('No renderer is found')
        return cls._renderer


def find_renderer(cls) -> AbstractRenderer:
    rendered_type = getattr(cls, 'rendered_type', None) or cls.__name__  # Check MRO names ??
    if _app.theme.renderers:
        return _app.theme.renderers.get(rendered_type, None) or _app.renderers.get(rendered_type, None)
    return _app.renderers.get(rendered_type, None)
