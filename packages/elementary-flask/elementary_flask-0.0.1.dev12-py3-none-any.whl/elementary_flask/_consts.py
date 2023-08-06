from os.path import abspath, join, dirname

MODULE_PATH = dirname(abspath(__file__))
TEMPLATE_FOLDER = join(MODULE_PATH, 'templates')
STATIC_FOLDER = join(MODULE_PATH, 'static')
