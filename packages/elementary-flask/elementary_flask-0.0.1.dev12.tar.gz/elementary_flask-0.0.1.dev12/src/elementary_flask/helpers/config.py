__all__ = ['HelperConfigException', 'set_helper_config', 'get_helper_config']

from flask import current_app, _app_ctx_stack

_default_config = None


class HelperConfigException(Exception):
    pass


def set_helper_config(config, force=False):
    global _default_config
    if _default_config is None or force:
        _default_config = config
    else:
        raise HelperConfigException('Helper config is already set')


def get_helper_config():
    ctx = _app_ctx_stack.top
    if ctx:
        return current_app.config
    if _default_config is None:
        raise HelperConfigException('Helper config is not set yet')
    return _default_config
