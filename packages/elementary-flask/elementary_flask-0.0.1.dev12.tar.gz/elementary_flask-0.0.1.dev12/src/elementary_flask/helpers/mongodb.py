__all__ = ['mongo_client', 'mongo_db', 'connect_mongoengine', 'get_mongo_config']

# from flask import current_app, _app_ctx_stack  # noqa
# MONGO_CLIENT_ATTRIBUTE_NAME = 'elementary_flask_mongo_client'
from .config import get_helper_config

_mongo_client = None


# def mongo_client():
#     ctx = _app_ctx_stack.top
#     if ctx is not None:
#         # current_app.teardown_appcontext(_teardown)
#         if not hasattr(ctx, MONGO_CLIENT_ATTRIBUTE_NAME):
#             setattr(ctx, MONGO_CLIENT_ATTRIBUTE_NAME, _mongo_client())
#             current_elementary_flask_app.append_teardown(_teardown)
#         return getattr(ctx, MONGO_CLIENT_ATTRIBUTE_NAME)


def mongo_client():
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = _get_mongo_client()
    return _mongo_client


def mongo_db(db):
    return mongo_client()[db]


def get_mongo_config(config=None):
    app_config = config or get_helper_config()
    elementary_config = app_config.setdefault('ELEMENTARY_FLASK', dict())
    mongo_config = elementary_config.setdefault('mongodb', False)
    debug = app_config.setdefault('DEBUG', True)

    if mongo_config is not False:
        if not mongo_config:
            elementary_config['mongodb'] = dict()
            mongo_config = elementary_config['mongodb']

        mongo_config.setdefault('db', app_config.get('ELEMENTARY_FLASK_APP_NAME', 'test_app').lower())

        if 'url' not in mongo_config:
            host = mongo_config.setdefault('host', 'localhost' if debug else 'mongo')
            port = mongo_config.setdefault('port', 27017)
            # db = db or mongo_config.setdefault(
            #     'db',
            #     app_config.setdefault('ELEMENTARY_FLASK_APP_NAME', 'test_app').lower()
            # )
            # mongo_config.setdefault('url', "mongodb://%s:%d/%s" % (host, port, db))
            mongo_config.setdefault('url', "mongodb://%s:%d/" % (host, port))

        # mongo_config.setdefault('connect_mongoengine', False)

    return mongo_config


def _get_mongo_client():
    mongo_config = get_mongo_config()
    if mongo_config:
        import pymongo  # noqa
        return pymongo.MongoClient(mongo_config['url'])


def connect_mongoengine(db=None, alias=None, **kwargs):
    mongo_config = get_mongo_config()
    db = db or mongo_config['db']
    if mongo_config and mongo_config.get('connect_mongoengine', False):
        import mongoengine  # noqa
        if alias is None:
            mongoengine.connect(host=mongo_config['url'] + db, **kwargs)
        return mongoengine.connect(host=mongo_config['url'] + db, alias=alias, **kwargs)

# def _teardown(exception):
#     ctx = _app_ctx_stack.top
#     if ctx and hasattr(ctx, MONGO_CLIENT_ATTRIBUTE_NAME):
#         getattr(ctx, MONGO_CLIENT_ATTRIBUTE_NAME).close()
