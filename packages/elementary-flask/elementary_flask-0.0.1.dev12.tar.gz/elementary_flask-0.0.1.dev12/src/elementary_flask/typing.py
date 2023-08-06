import typing as _typing
from typing import Optional, List, Dict, AnyStr, Set, Iterable

from markupsafe import Markup
import flask.typing as _flask_typing

ResponseReturnValue = _flask_typing.ResponseReturnValue
OptionalList = Optional[List]
OptionalDict = Optional[Dict]
OptionalSet = Optional[Set]
OptionalAnyStr = Optional[AnyStr]
OptionalStr = Optional[str]
Union = _typing.Union
Callable = _typing.Callable
Any = _typing.Any
Tuple = _typing.Tuple
Iterable = Iterable

# MarkupPlus = "MarkupPlus"
# RenderReturnValue = Union[MarkupPlus, Optional[str], Markup]
RenderReturnValue = Union[str, Markup]
Renderable = "Renderable"

# class Renderable:
#     def render(self, **options) -> RenderReturnValue:
#         raise NotImplementedError()


StatusCode = _flask_typing.StatusCode
HeadersValue = _flask_typing.HeadersValue
Block = Union[RenderReturnValue, "Renderable", Callable]
BlocksDict = Dict[str, Block]
BlocksInit = Union[Block, BlocksDict]
PageErrorResponseInit = Union[StatusCode, Tuple[StatusCode, str], Tuple[StatusCode, HeadersValue],
                              Tuple[StatusCode, str, HeadersValue]]
PageResponseInit = Union[BlocksInit, Tuple[BlocksInit, StatusCode], Tuple[BlocksInit, StatusCode, HeadersValue],
                         Tuple[BlocksInit, HeadersValue], PageErrorResponseInit]

PageResponse = "PageResponse"
PageRouteReturnValue = Union[PageResponse, PageResponseInit]
ComponentIncludes = "ComponentIncludes"
# NavigationItem = Union["NavigationLink", "NavigationSeparator", "NavigationGroup"]
NavigationItem = "NavigationItem"
# NavigationData = List[NavigationItem]
# NavigationMap = "NavigationMap"
NavigationMapInit = Union["NavigationGroup", Iterable[NavigationItem]]
Navigation = "Navigation"
ContainerChildren = Union[Block, Iterable[Block]]
FormAction = "FormAction"
FormActionInit = Union[FormAction, Iterable[FormAction], "Form"]
FormResponseReturn = Union["FormResponse", FormActionInit]
AbstractWeakComponent = "AbstractWeakComponent"
AbstractRenderer = "AbstractRenderer"
RendererMapping = Dict[type, AbstractRenderer]
Renderer = Union[AbstractRenderer, Callable]
AbstractIcon = "AbstractIcon"
AbstractListing = "AbstractListing"
CronEntry = "CronEntry"
