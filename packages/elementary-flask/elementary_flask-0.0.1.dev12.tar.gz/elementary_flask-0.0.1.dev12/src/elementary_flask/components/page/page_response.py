__all__ = ['PageResponse', 'PageErrorResponse', 'make_page_response']
from dataclasses import dataclass, field

from elementary_flask.typing import Optional, BlocksInit, BlocksDict, HeadersValue, PageResponseInit
# from .component import ComponentIncludes, reduce_includes
from elementary_flask.utils.http_status import HTTP_STATUS_DICT
from .. import HTTPError


@dataclass()
class PageResponse:
    blocks_init: BlocksInit
    # component_includes: ComponentIncludes = field(init=False)
    # ns: SimpleNamespace = field(default_factory=SimpleNamespace)
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[str] = None
    author: Optional[str] = None
    viewport: Optional[str] = None
    headers: Optional[HeadersValue] = None
    status_code: Optional[int] = None
    status_code_msg: Optional[str] = None
    # status_code_error: bool = False
    page_layout: Optional[str] = None
    blocks: BlocksDict = field(init=False)

    def __post_init__(self):
        if not isinstance(self.blocks_init, dict):
            self.blocks = {'main': self.blocks_init}
        else:
            self.blocks = self.blocks_init
        # self.component_includes = reduce_includes(self.blocks.items())
        self.meta_tags = dict(description=self.description, keywords=self.keywords, author=self.author,
                              viewport=self.viewport)


class PageErrorResponse(PageResponse):
    def __init__(self, status_code, status_code_msg="", status_code_description="",
                 page_layout=None, headers=None, title=None):
        # TODO default status_code_msg for status_code
        if status_code_msg is None and status_code >= 400:
            status_code_msg = HTTP_STATUS_DICT.get(status_code, 'Error')

        if page_layout is None:
            page_layout = 'error'

        super(PageErrorResponse, self).__init__(HTTPError(status_code=status_code,
                                                          status_code_name=status_code_msg,
                                                          status_code_description=status_code_description),
                                                status_code=status_code,
                                                status_code_msg=status_code_msg,
                                                page_layout=page_layout, title=title,
                                                headers=headers)


def make_page_response(response_init: PageResponseInit, page_layout=None):
    if not isinstance(response_init, tuple):
        response_init = (response_init,)

    block_init = None
    headers = None
    status_code = None
    status_code_msg = None
    only_status_code = isinstance(response_init[0], int)

    if only_status_code and len(response_init) == 3:
        status_code, status_code_msg, headers = response_init
    elif only_status_code and len(response_init) == 2 and isinstance(response_init[1], str):
        status_code, status_code_msg = response_init
    elif only_status_code and len(response_init) == 2:
        status_code, headers = response_init
    elif only_status_code:
        status_code = response_init[0]
    elif len(response_init) == 3:
        block_init, status_code, headers = response_init
    elif len(response_init) == 2 and isinstance(response_init[1], int):
        block_init, status_code = response_init
    elif len(response_init) == 2:
        block_init, headers = response_init
    else:
        block_init = response_init[0]

    if status_code is not None and status_code >= 400:
        return PageErrorResponse(status_code, page_layout=page_layout,
                                 status_code_msg=status_code_msg, headers=headers)
    else:
        return PageResponse(block_init, page_layout=page_layout, status_code=status_code, headers=headers)
