__all__ = ['ElementaryScaffold', 'setupmethod']

import re

from flask.scaffold import setupmethod
from flask import Blueprint

import elementary_flask.typing as t
from elementary_flask.components import get_icon, NavigationLink, wrap_form_cls, form_endpoint_wrapper, \
    page_view_wrapper
from elementary_flask.cron import CronEntry

_form_name_validator = re.compile(r'^[a-z0-9_]+$', re.IGNORECASE)

URL_PREFIXES = ('form', 'listing', 'stateful', 'api')
URL_PREFIXES_EQUALS = tuple('/' + p for p in URL_PREFIXES)
URL_PREFIXES_STARTSWITH = tuple(p + '/' for p in URL_PREFIXES_EQUALS)


class ElementaryScaffoldNamespace:
    def __init__(self):
        self.navigation_map = list()
        self.page_view_functions = dict()
        self.crontab = list()
        # self.api_bp = _f.Blueprint('api', __name__, url_prefix='/api')
        # self.form_bp = _f.Blueprint('form', __name__, url_prefix='/form')
        # self.listing_bp = _f.Blueprint('listing', __name__, url_prefix='/listing')
        # self.stateful_bp = _f.Blueprint('stateful', __name__, url_prefix='/stateful')


class ElementaryScaffold:
    def __init__(self):
        self.elementary_ns = ElementaryScaffoldNamespace()
        self.endpoint_prefix = None

    @setupmethod
    def route_page(self, rule: str, endpoint: t.OptionalStr = None,
                   page_layout='default',
                   navigation=False,
                   navigation_title=None,
                   navigation_params=None,
                   navigation_icon: t.Union[str, t.AbstractIcon] = None,
                   **options):
        """Decorate a page view function to register it with the given URL
        rule and options.

        .. code-block:: python

            @app.route_page("/")
            def index():
                return "Hello, World!"

        :param rule: The URL rule string.
        :param endpoint: Name for the route. Default value: the name of function.
        :param page_layout: Name of :class:`PageLayout` that renders the response. Default value: ``'default'``.
        :param navigation: Add the page to navigation. Default value: ``None``.
        :param navigation_title: The page title used in navigation.
        :param navigation_icon: The page icon used in navigation.
        :param navigation_params:
        :param options: Extra options passed to the Flask object.
        """
        return self._route_page(rule, endpoint=endpoint,
                                page_layout=page_layout,
                                navigation=navigation,
                                navigation_title=navigation_title,
                                navigation_params=navigation_params,
                                navigation_icon=navigation_icon,
                                methods=None,
                                **options)

    def _route_page(self, rule: str, endpoint: t.OptionalStr = None,
                    page_layout='default',
                    navigation=False,
                    navigation_title=None,
                    navigation_params=None,
                    navigation_icon: t.Union[str, t.AbstractIcon] = None,
                    methods=None,
                    **options):

        def decorator(f):
            # _ep = endpoint if endpoint is not None else cls.__name__ + '.__init__'rende
            _ep = endpoint if endpoint is not None else f.__name__
            if navigation:
                _nt = navigation_title
                if not _nt:
                    _nt = _ep.replace('_', ' ').strip()
                    _nt = _nt[0].upper() + _nt[1:]
                _ni = get_icon(navigation_icon)
                self.elementary_ns.navigation_map.append(
                    NavigationLink(title=_nt, endpoint=lambda: self.endpoint_prefix + _ep, params=navigation_params,
                                   icon=_ni))

            options['methods'] = ['GET']
            self._register_endpoint_function(rule, f, _ep, page_view_wrapper, options,
                                             wrapper_kwargs=dict(default_page_layout=page_layout))
            return f

        return decorator


    @setupmethod
    def listing(self,
                # name: t.Optional[str] = None,
                # rendering_type: str = 'stateful',
                **options: t.Any,
                ):
        """Creates a new :class:`Form` and uses the decorated function as
        callback.

        :param options: extra options passed to flask add_url_rule.
        """

        # if rendering_type not in FORM_RENDERING_TYPES:
        #     rendering_type = 'default'

        def decorator(cls):
            # n = name or cls.__name__
            n = cls.__name__
            rule = n
            if not _form_name_validator.match(rule):
                raise ValueError('Forbidden value for rule: ' + rule)

            setattr(cls, 'elementary_flask_action_endpoint', lambda cls_self: self.endpoint_prefix + n)

            # register form endpoint
            options['methods'] = ['POST']
            self._register_endpoint_function('/listing/' + rule, cls, n, form_endpoint_wrapper, options)
            return cls

        return decorator

    @setupmethod
    def form(self,
             name: t.Optional[str] = None,
             rendering_type: str = 'stateful',
             **options: t.Any,
             ):
        """Creates a new :class:`Form` and uses the decorated function as
        callback.

        :param name: the name of the form. Default: class name.
        :param rendering_type: Form rendering types. Default: 'default'.
        :param options: extra options passed to flask add_url_rule.
        """

        # if rendering_type not in FORM_RENDERING_TYPES:
        #     rendering_type = 'default'

        def decorator(cls):
            n = name or cls.__name__
            rule = n
            if not _form_name_validator.match(rule):
                raise ValueError('Forbidden value for rule: ' + rule)

            # Make class renderable
            wrap_form_cls(cls, form_id=n, rendering_type=rendering_type, scaffold=self)

            # register form endpoint
            options['methods'] = ['POST']
            self._register_endpoint_function('/form/' + rule, cls, n, form_endpoint_wrapper, options)
            return cls

        return decorator

    def _register_endpoint_function(self, rule, func, endpoint, wrapper_function, add_url_options,
                                    wrapper_kwargs=None, validate_rule=False):
        if validate_rule and _validate_rule(rule):
            raise ValueError(f"The following rule prefixes are reserved for "
                             f"ElementaryFlask and ElementaryBluePrint: {URL_PREFIXES_EQUALS}")
        wrapper_kwargs = wrapper_kwargs or dict()
        old_func, old_wrapped = self.elementary_ns.page_view_functions.get(endpoint, (None, None))
        if old_func is not None and old_func != func:
            raise AssertionError(
                "Endpoint function mapping is overwriting an existing"
                f" endpoint function: {endpoint}"
            )
        elif old_func is None:
            self.elementary_ns.page_view_functions[endpoint] = func, wrapper_function(func, **wrapper_kwargs)

        wrapped = self.elementary_ns.page_view_functions[endpoint][1]

        self.add_url_rule(rule, endpoint, wrapped, **add_url_options)  # noqa

    @setupmethod
    def cron(self, expr_format: str, /, *, name: str = None, hash_id=None, args=None, kwargs=None):
        def decorator(f):
            n = name or f.__name__
            self.elementary_ns.crontab.append(
                CronEntry(n, expr_format, task=f, hash_id=hash_id, args=args, kwargs=kwargs))
            return f

        return decorator

    # def endpoint_prefix(self):
    #     raise NotImplementedError()
    #     # if isinstance(self, Blueprint):
    #     #     return self.name + '.'
    #     # return ''


def _validate_rule(rule):
    return all(not rule.startswith(p) for p in URL_PREFIXES_STARTSWITH) and all(rule != p for p in URL_PREFIXES_EQUALS)
