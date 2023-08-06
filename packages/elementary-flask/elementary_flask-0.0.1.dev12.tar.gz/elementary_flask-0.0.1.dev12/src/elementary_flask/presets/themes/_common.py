from os.path import join

from elementary_flask._consts import TEMPLATE_FOLDER
from elementary_flask.utils import Jinja2Env

THEMES_FOLDER = join(TEMPLATE_FOLDER, 'themes')


def make_jinja2_theme_env(theme_name, loader=None, autoescape=True, auto_reload=True, **options):
    templates_path = join(THEMES_FOLDER, theme_name)
    return Jinja2Env(templates_path=templates_path, loader=loader, autoescape=autoescape, auto_reload=auto_reload,
                     **options)
