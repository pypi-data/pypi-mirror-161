from flask import render_template as flask_render_template
from markupsafe import Markup


def render_template(
        template_name_or_list,
        **context):
    return Markup(flask_render_template(template_name_or_list, **context))
