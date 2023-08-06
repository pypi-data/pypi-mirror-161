from ._includes import Dependency, JavascriptDependencyLink

DEFAULT_ALPINEJS_VERSION = (3, 9, 1)
DEFAULT_ALPINEJS_DEPENDENCY = Dependency(
    name='alpinejs',
    version=DEFAULT_ALPINEJS_VERSION,
    links=[JavascriptDependencyLink(
        link="https://unpkg.com/alpinejs@3.9.1/dist/cdn.min.js",
        include_position='head',
        defer=True,
    )]
)
