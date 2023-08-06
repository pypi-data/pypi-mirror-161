__all__ = ["ElementaryBluePrint"]

from flask import Blueprint, Flask

from elementary_flask.components import NavigationGroup, get_icon
from .scaffold import ElementaryScaffold


class ElementaryBluePrint(Blueprint, ElementaryScaffold):
    def __init__(self, name, import_name, *args,
                 navigation_title=None, navigation_icon=None,
                 connect_mongoengine_db=None, connect_mongoengine_alias=None, connect_mongoengine_kwargs=None,
                 **kwargs):
        Blueprint.__init__(self, name, import_name, *args, **kwargs)
        ElementaryScaffold.__init__(self)
        self.navigation_title = navigation_title or name
        self.navigation_icon = get_icon(navigation_icon)
        self.connect_mongoengine_db = connect_mongoengine_db
        self.connect_mongoengine_alias = connect_mongoengine_alias or connect_mongoengine_db
        self.connect_mongoengine_kwargs = connect_mongoengine_kwargs or dict()

    def register(self, app, options: dict) -> None:
        from elementary_flask.app import ElementaryFlask
        flask_app, elementary_app = None, None
        if isinstance(app, Flask):
            flask_app = app
            if hasattr(app, 'elementary_flask'):
                elementary_app = app.elementary_flask
        elif isinstance(app, ElementaryFlask):
            elementary_app = app
            flask_app = elementary_app.flask_app
        else:
            raise ValueError('Unknown app type')

        if not flask_app:
            raise ValueError('Flask App is not initialized yet. None value provided')

        name_prefix = options.get("name_prefix", "")
        self_name = options.get("name", self.name)
        self.endpoint_prefix = f"{name_prefix}.{self_name}.".lstrip('.')
        self.elementary_bp_register(elementary_app)
        super(ElementaryBluePrint, self).register(flask_app, options)

        # Mongo Engine connect
        if self.connect_mongoengine_db:
            from elementary_flask.helpers.mongodb import connect_mongoengine
            with flask_app.app_context():
                connect_mongoengine(db=self.connect_mongoengine_db, alias=self.connect_mongoengine_alias,
                                    **self.connect_mongoengine_kwargs)

    def elementary_bp_register(self, elementary_app):
        elementary_app.crontab.extend(self.elementary_ns.crontab)
        elementary_app.extend_navigation_map(
            NavigationGroup(self.navigation_title,
                            icon=self.navigation_icon,
                            items_list=self.elementary_ns.navigation_map)
        )

    # def endpoint_prefix(self):
    #     return f"{self.name_prefix}.{self.name}."
