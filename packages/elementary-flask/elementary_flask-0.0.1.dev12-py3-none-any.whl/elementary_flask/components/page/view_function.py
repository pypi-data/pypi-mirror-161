__all__ = ['page_view_wrapper']

from werkzeug.wrappers import Response

from elementary_flask.globals import current_elementary_flask_app as _app
import elementary_flask.typing as t
from .page_response import PageResponse, PageErrorResponse, make_page_response


def page_view_wrapper(f: t.Callable[..., t.PageRouteReturnValue], default_page_layout='default'):
    def _wrap(*args, **kwargs) -> t.ResponseReturnValue:
        page_response = f(*args, **kwargs)
        if isinstance(page_response, Response):
            return page_response

        if not isinstance(page_response, PageResponse):
            page_response = make_page_response(page_response)
        pl = page_response.page_layout if page_response.page_layout is not None else default_page_layout
        # try:
        if isinstance(page_response, PageErrorResponse):
            render_response = _app.get_layout('error').render(page_response=page_response)
        else:
            render_response = _app.get_layout(pl).render(page_response=page_response)

        return render_response

    return _wrap
