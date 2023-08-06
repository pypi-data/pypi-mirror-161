from elementary_flask.components import Theme, LayoutMapping
from elementary_flask.includes import ComponentIncludes, Dependency, CSSDependencyLink, JavascriptDependencyLink
from elementary_flask.includes import adminlte_dependency
from .layouts import AdminLTEDefaultLayout
from .renderers import render_http_error, render_navigation


class AdminLTETheme(Theme):
    bootstrap_dependency = adminlte_dependency
    default_includes = ComponentIncludes([
        Dependency('source_sans_pro_font',
                   links=[CSSDependencyLink(
                       "https://fonts.googleapis.com/css?family=Source+Sans+Pro:300,400,400i,700&display=fallback")]
                   ),
        Dependency('fontawesome-free', version='5.15.3',
                   links=[CSSDependencyLink(
                       "https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@5.15.3/css/all.min.css")]
                   ),
        Dependency('adminlte', version='3.2.0',
                   links=[JavascriptDependencyLink(
                       "https://cdn.jsdelivr.net/npm/admin-lte@3.2.0/dist/js/adminlte.min.js")
                   ]
                   )
    ])
    layouts_mapping = LayoutMapping(
        default=AdminLTEDefaultLayout(),
        card=AdminLTEDefaultLayout(card_container=True),
    )
    renderers = {
        "HTTPError": render_http_error,
        "Navigation": render_navigation
    }
