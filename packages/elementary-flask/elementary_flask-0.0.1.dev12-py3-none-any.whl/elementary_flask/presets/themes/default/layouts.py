from types import SimpleNamespace

from elementary_flask.components import EmptyPageLayout  # , AbstractNavigation
from ._jinja2_env import jinja2_env


# from .components import BootstrapTopNavigation


class TopNavigationLayout(EmptyPageLayout):
    def __init__(self, additional_includes=None, block_names=None):  # , navigation: AbstractNavigation = None):
        super(TopNavigationLayout, self).__init__(additional_includes=additional_includes,
                                                  block_names=block_names)

        # self.navigation = navigation or BootstrapTopNavigation()

    def render_body_tag(self, ns: SimpleNamespace) -> str:
        return jinja2_env.render_template('layouts/default_body.html',
                                          **ns.__dict__)  # navigation=self.navigation, **ns.__dict__)
