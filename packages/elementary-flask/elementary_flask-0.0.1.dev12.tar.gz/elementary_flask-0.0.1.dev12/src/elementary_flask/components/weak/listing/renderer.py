__all__ = ['default_listing_render']

from elementary_flask.globals import current_elementary_flask_app as _app
from elementary_flask.typing import AbstractListing, RenderReturnValue


def default_listing_render(listing: AbstractListing, /, **options) -> RenderReturnValue:
    listing.init_listing_cls()
    items, count_str, next_page, previous_page = listing.list_items_request()
    ret = _app.core_jinja_env.render_template("listing/default_listing.html",
                                              listing=listing,
                                              items=items, count_str=count_str,
                                              next_page=next_page, previous_page=previous_page,
                                              )
    listing.view_page_kwargs = None
    return ret
