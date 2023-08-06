from elementary_flask.components import HTTPError
from elementary_flask.typing import RenderReturnValue, Navigation
from ._jinja2_env import jinja2_env


def render_http_error(http_error: HTTPError, /, **options) -> RenderReturnValue:
    return jinja2_env.render_template('components/error.html',
                                      error_message=http_error.status_code_name,
                                      error_description=http_error.status_code_description,
                                      status_code=http_error.status_code,
                                      error_color='danger' if http_error.status_code >= 500 else 'warning',
                                      )


def render_navigation(navigation: Navigation, /, **options) -> RenderReturnValue:
    return jinja2_env.render_template('components/navigation.html',
                                      navigation=navigation,
                                      )
