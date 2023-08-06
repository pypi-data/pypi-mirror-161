import os
from types import SimpleNamespace

import flask as _f
import yaml
from werkzeug.exceptions import HTTPException
from flask_caching import Cache

import elementary_flask.typing as t
from ._consts import STATIC_FOLDER, TEMPLATE_FOLDER
from .components import FavIcon, Theme, LayoutMapping, \
    EmptyPageLayout, default_form_render, AbstractNavigationProvider, StaticNavigationProvider, Navigation, \
    PageErrorResponse
from .cron import cron_endpoint, CronEntry
from .includes import DEFAULT_BOOTSTRAP_VERSION, DEFAULT_ALPINEJS_DEPENDENCY, ComponentIncludes
from .presets.themes import DefaultTheme
from .blueprint import ElementaryScaffold


class ElementaryFlask(ElementaryScaffold):
    def __init__(self, name, flask_app=None, /, *,
                 create_flask_app=False, flask_app_options=None,
                 default_includes=None, default_meta_tags=None, default_title=None, icons: t.List[FavIcon] = None,
                 theme: t.Optional[t.Union[Theme, str]] = None, include_bootstrap=True,
                 navigation_map: dict = None,
                 navigation_provider: AbstractNavigationProvider = None,
                 include_alpinejs=True,
                 alpinejs_dependency=None,
                 logo_src=None,
                 renderers=None,
                 crontab: t.Iterable[CronEntry] = None,
                 cache_config=None,
                 cache_with_jinja2_ext=None,
                 **options):

        ElementaryScaffold.__init__(self)
        self._init = False
        self.name = name
        self.endpoint_prefix = ""

        self.flask_app = flask_app
        if not self.flask_app and create_flask_app:
            flask_app_options = flask_app_options or dict()
            self.flask_app = _f.Flask(name, **flask_app_options)

        self.flask_config = None
        self.core_bp = _f.Blueprint('core', __name__, url_prefix='/core',
                                    static_folder=STATIC_FOLDER, template_folder=TEMPLATE_FOLDER)

        # App Config
        self.config = SimpleNamespace()

        # Default includes
        self.config.default_includes = default_includes or ComponentIncludes()

        # Logo & Favicons
        self.config.logo_src = logo_src or "/core/static/img/logo.png"
        self.config.icons = icons or [FavIcon(href=self.config.logo_src, mimetype="image/png")]

        # Metas
        if default_meta_tags:
            self.config.default_meta_tags = default_meta_tags
        else:
            self.config.default_meta_tags = dict()

        if 'viewport' not in self.config.default_meta_tags:
            self.config.default_meta_tags['viewport'] = 'width=device-width, initial-scale=1'

        self.config.default_title = default_title if default_title is not None else name

        # AlpineJS
        if include_alpinejs or alpinejs_dependency:
            alpinejs_dependency = alpinejs_dependency or DEFAULT_ALPINEJS_DEPENDENCY
            self.config.default_includes.dependencies.insert(0, alpinejs_dependency)

        # Theme
        if theme and isinstance(theme, Theme):
            self.theme = theme
        elif theme == 'adminlte':
            from elementary_flask.presets.themes import AdminLTETheme
            self.theme = AdminLTETheme()
        else:
            # bootstrap_theme = options.get('bootstrap_theme', None)
            bootstrap_version = options.get('bootstrap_version', DEFAULT_BOOTSTRAP_VERSION)
            bootstrap_dependency = options.get('bootstrap_dependency', None)
            theme_default_includes = options.get('theme_default_includes', None)
            theme_layouts_mapping = options.get('theme_layouts_mapping', None)
            self.theme = DefaultTheme(bootstrap_version=bootstrap_version, bootstrap_theme=theme,
                                      layouts_mapping=theme_layouts_mapping,
                                      include_bootstrap=include_bootstrap,
                                      bootstrap_dependency=bootstrap_dependency,
                                      default_includes=theme_default_includes)

        self.config.default_includes += self.theme.default_includes

        # ElementaryFlask js & css
        self.config.default_includes += ComponentIncludes(
            js_includes={'/core/static/elementary_flask.js'},
            css_includes={'/core/static/elementary_flask.css'},
        )

        # Default Layout Mapping
        self.layout_mapping = LayoutMapping(
            default=EmptyPageLayout()
        )

        # Core jinja2 environment
        from elementary_flask.utils.jinja2 import Jinja2Env
        self.core_jinja_env = Jinja2Env(TEMPLATE_FOLDER)

        # Navigation
        self.config.navigation_map = navigation_map or []
        self.elementary_ns.navigation_map = self.config.navigation_map
        self.config.navigation_provider = navigation_provider or StaticNavigationProvider(self.config.navigation_map)
        self.config.navigation = Navigation()

        # Logger
        self.logger = None

        # Renderers
        self.renderers = dict(DEFAULT_RENDERERS)
        if renderers:
            self.renderers.update(renderers)

        # Crontab & cron endpoint rule
        self.crontab = self.elementary_ns.crontab  # Default crons
        if crontab:
            self.crontab.extend(crontab)

        self.core_bp.add_url_rule('/cron', 'cron', cron_endpoint)

        self.redis = None
        self._teardown_functions = list()

        # Cache
        self.cache = None
        self.config.cache_config = cache_config or dict()
        self.config.cache_with_jinja2_ext = cache_with_jinja2_ext

        # init app
        if self.flask_app:
            self.init_app(self.flask_app)

    def init_app(self, flask_app, /, ):
        from elementary_flask.utils.jinja2 import JINJA2_FILTERS_UPDATES, JINJA2_GLOBALS_UPDATES
        if self._init:
            return
        self.flask_app = flask_app
        self.flask_app.elementary_flask = self
        self.flask_app.update_template_context(dict(elementary_flask_config=self.config))
        self.flask_app.jinja_env.globals.update(**JINJA2_GLOBALS_UPDATES)
        self.flask_app.jinja_env.filters.update(**JINJA2_FILTERS_UPDATES)
        self.flask_config = self.flask_app.config

        # Registering Blueprints
        self.flask_config.from_file('app.config.yml', load=yaml.safe_load)
        self.flask_config.setdefault('ELEMENTARY_FLASK_APP_NAME', self.name)
        self.flask_config['DEBUG'] = os.environ.get('ELEMENTARY_DEBUG', 'False') == 'True'
        self.flask_app.register_blueprint(self.core_bp)

        # Error handler
        @self.flask_app.errorhandler(HTTPException)
        def handle_exception(e):
            """Renders the HTTP exception."""
            from elementary_flask.globals import current_elementary_flask_app as _app
            return _app.get_layout('error').render(
                page_response=PageErrorResponse(e.code, e.name, e.description)
            )

        # Teardown
        self.flask_app.teardown_appcontext(self.teardown)

        # logging level
        self.logger = self.flask_app.logger

        # Debug
        if self.flask_config['DEBUG']:
            self._set_debug_env()

        # Connect mongoengine
        from elementary_flask.helpers import set_helper_config, connect_mongoengine, get_redis_config
        set_helper_config(self.flask_config)
        with self.flask_app.app_context():
            connect_mongoengine()
            _rc = get_redis_config()
            # print(_rc)

        # Cache
        self.config.cache_config.setdefault('CACHE_TYPE', 'RedisCache')
        if _rc.get('url', None):
            self.config.cache_config.setdefault('CACHE_REDIS_URL', _rc.get('url'))
        else:
            self.config.cache_config.setdefault('CACHE_REDIS_HOST', _rc.get('host'))
            self.config.cache_config.setdefault('CACHE_REDIS_PORT', _rc.get('port'))
            self.config.cache_config.setdefault('CACHE_REDIS_DB', _rc.get('db'))
        if _rc.get('password', None):
            self.config.cache_config.setdefault('CACHE_REDIS_PASSWORD', _rc.get('password'))
        self.cache = Cache(with_jinja2_ext=self.config.cache_with_jinja2_ext, config=self.config.cache_config)
        self.cache.init_app(flask_app)

        self._init = True

    def _set_debug_env(self):
        import logging
        self.logger.setLevel(logging.DEBUG)
        self.flask_config['ELEMENTARY_FLASK_RENDER_ERROR_STRATEGY'] = 'raise'

    def run(self, host=None, port=None, debug=None, load_dotenv=True, **kwargs):
        # self.init_app(self.flask_app, debug=debug)
        if debug:
            os.environ['ELEMENTARY_DEBUG'] = 'True'
            self._set_debug_env()

        # Run flask app
        self.flask_app.run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **kwargs)

    def get_layout(self, layout_name):
        return self.theme.layouts_mapping.get_layout(layout_name)

    def render_core_template(self, template_name, **kwargs):
        return self.core_jinja_env.render_template(template_name, **kwargs)

    def set_navigation_provider(self, navigation_provider: AbstractNavigationProvider):
        self.config.navigation_provider = navigation_provider

    def extend_navigation_map(self, *items, clear_old=False):
        if clear_old:
            self.config.navigation_map.clear()
        self.config.navigation_map.extend(items)

    @staticmethod
    def url_for(endpoint: str, **values: t.Any) -> str:
        return _f.url_for(endpoint, **values)

    # def __call__(self, environ: dict, start_response: t.Callable) -> t.Any:
    #     self.init_app()
    #     return self.flask_app(environ=environ, start_response=start_response)

    def add_url_rule(
            self,
            rule: str,
            endpoint: t.Optional[str] = None,
            view_func: t.Optional[t.Callable] = None,
            provide_automatic_options: t.Optional[bool] = None,
            **options: t.Any,
    ) -> None:
        return self.flask_app.add_url_rule(rule, endpoint=endpoint, view_func=view_func,
                                           provide_automatic_options=provide_automatic_options, **options)

    def register_blueprint(self, blueprint, **options: t.Any) -> None:
        return self.flask_app.register_blueprint(blueprint, **options)

    def _is_setup_finished(self) -> bool:
        if self.flask_app is None:
            raise ValueError('setup method called before Flask App is init')
        return self.flask_app._is_setup_finished()

    def teardown(self, exception):
        for f in self._teardown_functions:
            try:
                f(exception)
            except Exception as e:
                pass  # TODO

    def append_teardown(self, func):
        self._teardown_functions.append(func)


DEFAULT_RENDERERS = {
    'Form': default_form_render
}
