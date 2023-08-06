from flask.globals import LocalProxy, current_app


def _find_app():
    return current_app.elementary_flask  # noqa


def _find_cache():
    return current_app.elementary_flask.cache  # noqa


current_elementary_flask_app: "ElementaryFlask" = LocalProxy(_find_app)  # type: ignore
current_elementary = current_elementary_flask_app
cache = LocalProxy(_find_cache)  # type: ignore
