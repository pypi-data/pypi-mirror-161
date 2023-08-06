from elementary_flask.components import EmptyPageLayout
from ._jinja2_env import jinja2_env


class AdminLTEDefaultLayout(EmptyPageLayout):
    def __init__(self, card_container=False):
        super(AdminLTEDefaultLayout, self).__init__()
        self.card_container = card_container

    def render_body_tag(self, page_response, **options) -> str:
        return jinja2_env.render_template('layouts/default_body.html',
                                          card_container=self.card_container,
                                          page_response=page_response,
                                          body_includes=self.reduce_includes().render_body_includes()
                                          )
