__all__ = ['AbstractNavigationProvider', 'DefaultNavigationProvider', 'StaticNavigationProvider']

from abc import ABC, abstractmethod

from elementary_flask.globals import current_elementary_flask_app as _app
from elementary_flask.typing import NavigationMapInit


class AbstractNavigationProvider(ABC):
    @abstractmethod
    def generate_navigation(self) -> NavigationMapInit:
        raise NotImplementedError()


class DefaultNavigationProvider(AbstractNavigationProvider):
    def generate_navigation(self) -> NavigationMapInit:
        return _app.config.navigation_provider.generate_navigation()


class StaticNavigationProvider(AbstractNavigationProvider):
    def __init__(self, navigation_map):
        super(StaticNavigationProvider, self).__init__()
        self.navigation_map = navigation_map

    def generate_navigation(self) -> NavigationMapInit:
        return self.navigation_map
