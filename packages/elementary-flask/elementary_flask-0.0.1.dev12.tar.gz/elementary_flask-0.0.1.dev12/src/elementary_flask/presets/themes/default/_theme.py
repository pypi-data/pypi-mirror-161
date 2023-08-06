from elementary_flask.components import LayoutMapping, EmptyPageLayout
from elementary_flask.components import Theme
from elementary_flask.includes import DEFAULT_BOOTSTRAP_VERSION, make_bootstrap_dependency
from .layouts import TopNavigationLayout


class DefaultTheme(Theme):
    def __init__(self, bootstrap_version=DEFAULT_BOOTSTRAP_VERSION, bootstrap_theme=None, layouts_mapping=None,
                 include_bootstrap=True, bootstrap_dependency=None, default_includes=None):
        if not bootstrap_dependency and include_bootstrap:
            bootstrap_dependency = make_bootstrap_dependency(version=bootstrap_version, theme=bootstrap_theme)
        if not layouts_mapping:
            layouts_mapping = LayoutMapping(
                default=TopNavigationLayout() if include_bootstrap else EmptyPageLayout()
            )
        self.bootstrap_dependency = bootstrap_dependency
        self.default_includes = default_includes
        self.layouts_mapping = layouts_mapping
        super(DefaultTheme, self).__init__()
