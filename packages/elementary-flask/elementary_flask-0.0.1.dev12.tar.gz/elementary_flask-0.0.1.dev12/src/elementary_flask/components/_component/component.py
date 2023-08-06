__all__ = ['Renderable', 'AbstractComponent', 'render', 'RenderException']

from abc import ABC, abstractmethod
from collections.abc import Mapping, Iterable
# from .markup_plus import MarkupPlus, RenderException # , RenderError,
from markupsafe import Markup

from elementary_flask.typing import RenderReturnValue, Block
from elementary_flask.globals import current_elementary


class Renderable(ABC):
    """
    An Interface for renderable objects
    """

    @abstractmethod
    def render(self, **options) -> RenderReturnValue:
        """Return the rendered object as a string or :class:`RenderResponse` object.

        :param options: namespace used in rendering the object. May be passed to the template engine.
        """
        raise NotImplementedError()


class AbstractComponent(Renderable):
    """
    AbstractComponent
    """
    error_strategy = 'safe'
    cache_strategy = 'none'  # init_options, init, options, none

    # _init_values = tuple()

    # component_includes = None

    # def __init__(self, component_includes: ComponentIncludes = None):
    #     # self.app =
    #     # self.app = current_elementary_flask_app
    #     # self.app_config = self.app.config
    #     if component_includes:
    #         self.component_includes = component_includes
    #     # TODO: bootstrap components (get version from current app, raise if not included)

    @abstractmethod
    def render(self, /, format_spec=None, **options) -> RenderReturnValue:
        raise NotImplementedError()

    # def _render(self, /, **options) -> RenderReturnValue: TODO cache
    #     if self.cache_strategy == 'none':
    #         return self.__render(**options)
    #
    #     cache_key = self._get_cache_key(**options)
    #     ret = cache.get(cache_key)
    #     if ret is None:
    #         ret = self.__render(**options)
    #         cache.set(cache_key, ret, timeout=self.cache_timeout)
    #     return ret

    # def _get_cache_key(self, **options):
    #     if self.cache_strategy == 'init_options':
    #         return id(self), self._init_values, options
    #     if self.cache_strategy == 'init':
    #         return id(self), self._init_values
    #     if self.cache_strategy == 'options':
    #         return id(self), options
    #     return None

    # def __render(self, /, format_spec=None, **options) -> RenderReturnValue: # TODO cache: rename to __render
    def _render(self, /, format_spec=None, **options) -> RenderReturnValue:
        if format_spec is None:
            return self.render(**options)
        if format_spec in ('start', 'end', 'children') and hasattr(self, 'render_' + format_spec):
            return getattr(self, 'render_' + format_spec)(**options)
        return render(format_spec=format_spec, **options)

    def render_start(self, /, **options) -> RenderReturnValue:
        pass

    def render_end(self, /, **options) -> RenderReturnValue:
        pass

    def render_children(self, separator='\n', **options):
        return render(*self, separator=separator, **options)

    def __repr__(self):
        try:
            return self._render()
        except:
            return object.__repr__(self)

    def __iter__(self):
        yield from ()

    def __str__(self):
        return self._render()

    def __html__(self):
        return self._render()

    def __html_format__(self, format_spec=None):
        return self._render(format_spec=format_spec)

    def __call__(self, /, format_spec=None, **options) -> RenderReturnValue:
        return self._render(format_spec=format_spec, **options)

    def __add__(self, other):
        return ConcatenatedComponent(self, other)

    def __radd__(self, other):
        return ConcatenatedComponent(other, self)


class ConcatenatedComponent(AbstractComponent):
    def __init__(self, *items: Block, separator='\n'):
        self.items = items
        self.separator = separator

    def render(self, /, **options) -> RenderReturnValue:
        return render(*self.items, separator=self.separator, **options)

    def __add__(self, other):
        return ConcatenatedComponent(*self.items, other)

    def __radd__(self, other):
        return ConcatenatedComponent(other, *self.items)


def _render(block: Block, **options) -> RenderReturnValue:
    # if isinstance(block, str) or isinstance(block, MarkupPlus) or isinstance(block, Markup):
    if block is None:
        return ''
    if isinstance(block, str) or isinstance(block, Markup):
        return block
    try:
        if isinstance(block, Renderable) or callable(getattr(block, '_render', None)):
            return getattr(block, '_render')(**options)
        if callable(getattr(block, 'render', None)):
            return getattr(block, 'render')(**options)
        if callable(block):
            return block(**options)
        if hasattr(block, '__html_format__') and ('format_spec' in options or not hasattr(block, '__html__')):
            return block.__html_format__(options.get('format_spec', None))
        if hasattr(block, '__html__'):
            return block.__html__()
        if isinstance(block, int) or isinstance(block, float) or isinstance(block, bool):
            return repr(block)
        if isinstance(block, Iterable) and not isinstance(block, Mapping):
            return render(*block, **options)

    except RenderException:
        raise
    except Exception as e:
        if getattr(block, 'error_strategy', None) == 'safe' \
                and not current_elementary.flask_config.get('ELEMENTARY_FLASK_RENDER_ERROR_STRATEGY', None) == 'raise':
            return 'Error'
        # raise RenderException('Error while rendering: ', e)
        raise
    raise RenderException('Unsupported block type')


def render(*blocks: Block, separator=None, **options) -> RenderReturnValue:
    res = Markup()
    first = True
    no_separator = not separator
    for b in blocks:
        if b is None:
            continue
        if no_separator or first:
            res += _render(b, **options)
        else:
            res += separator + _render(b, **options)
        first = False
    return res


class RenderException(Exception):
    pass
