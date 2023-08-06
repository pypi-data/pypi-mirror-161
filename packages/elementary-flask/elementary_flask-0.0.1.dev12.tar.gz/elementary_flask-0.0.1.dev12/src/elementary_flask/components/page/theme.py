__all__ = ['Theme']

from abc import ABC

from elementary_flask.includes import BootstrapDependency, ComponentIncludes
from elementary_flask.typing import Optional, RendererMapping
from .page_layout import LayoutMapping


class Theme(ABC):
    bootstrap_dependency: Optional[BootstrapDependency] = None
    default_includes: Optional[ComponentIncludes] = None
    layouts_mapping: Optional[LayoutMapping] = None
    renderers: Optional[RendererMapping] = None

    def __init__(self):
        self.default_includes = self.default_includes or ComponentIncludes()
        if self.bootstrap_dependency:
            self.default_includes.dependencies.insert(0, self.bootstrap_dependency)
