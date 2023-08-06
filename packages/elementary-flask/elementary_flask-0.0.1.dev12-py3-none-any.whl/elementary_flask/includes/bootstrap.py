from ._includes import Dependency, create_dependency_links, BootstrapDependency, \
    JavascriptDependencyLink, CSSDependencyLink

BOOTSTRAP5 = (5, 1, 3)
BOOTSTRAP4 = (4, 6, 1)
DEFAULT_BOOTSTRAP_VERSION = BOOTSTRAP5
INCLUDED_BOOTSTRAP_VERSION = (BOOTSTRAP4, BOOTSTRAP5)
_bootstrap4_jquery_dependency = Dependency('jquery', version='3.5.1', links=[
    JavascriptDependencyLink('https://cdn.jsdelivr.net/npm/jquery@3.5.1/dist/jquery.min.js')
                             # integrity='sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj')
])
_bootstrap_js_links = {
    BOOTSTRAP4: JavascriptDependencyLink(
        'https://cdn.jsdelivr.net/npm/bootstrap@4.6.1/dist/js/bootstrap.bundle.min.js',
        integrity='sha384-fQybjgWLrvvRgtW6bFlB7jaZrFsaBXjsOMm/tB9LTS58ONXgqbR9W8oWht/amnpF'
    ),
    BOOTSTRAP5: JavascriptDependencyLink(
        'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js',
        integrity='sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p'
    )
}
_bootstrap4_dependency = BootstrapDependency(
    js_link=_bootstrap_js_links[BOOTSTRAP4],
    css_link=CSSDependencyLink(
        'https://cdn.jsdelivr.net/npm/bootstrap@4.6.1/dist/css/bootstrap.min.css',
        integrity='sha384-zCbKRCUGaJDkqS1kPbPd7TveP5iyJE0EjAuZQTgFLD2ylzuqKfdKlfG/eSrtxUkn'),
    version=BOOTSTRAP4,
    jquery_dependency=_bootstrap4_jquery_dependency
)
_bootstrap5_dependency = BootstrapDependency(
    js_link=_bootstrap_js_links[BOOTSTRAP5],
    css_link=CSSDependencyLink(
        'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css',
        integrity='sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3'),
    version=BOOTSTRAP5,
)
adminlte_dependency = BootstrapDependency(
    js_link=_bootstrap_js_links[BOOTSTRAP4],
    css_link=CSSDependencyLink('https://cdn.jsdelivr.net/npm/admin-lte@3.2.0/dist/css/adminlte.css'),
    version=BOOTSTRAP4,
    theme="adminlte",
    jquery_dependency=_bootstrap4_jquery_dependency,
)
#
_bootstrap_dependencies = {
    (BOOTSTRAP4, 'vanilla'): _bootstrap4_dependency,
    (BOOTSTRAP5, 'vanilla'): _bootstrap5_dependency,
}
BOOTSWATCH_THEMES = {
    BOOTSTRAP5: ['cerulean', 'cyborg', 'flatly', 'litera', 'lux', 'minty', 'pulse', 'regent', 'simplex', 'slate',
                 'spacelab', 'united', 'yeti', 'cosmo', 'darkly', 'journal', 'lumen', 'materia', 'morph', 'quartz',
                 'sandstone', 'sketchy', 'solar', 'superhero', 'vapor', 'zephyr'],
    BOOTSTRAP4: ['yeti', 'united', 'superhero', 'spacelab', 'solar', 'slate', 'sketchy', 'simplex', 'sandstone',
                 'pulse', 'minty', 'materia', 'lux', 'lumen', 'litera', 'journal', 'flatly', 'darkly', 'cyborg',
                 'cosmo', 'cerulean', ]
}


def make_bootstrap_dependency(version=None, theme=None,
                              links=None, css_includes=None, js_includes=None, dependencies=None):
    global _bootstrap_dependencies
    links = links or list()

    # Force version for custom boostrap themes
    if theme == 'adminlte':
        return adminlte_dependency

    _version = version or DEFAULT_BOOTSTRAP_VERSION
    create_dependency_links(links, css_includes=css_includes, js_includes=js_includes)

    if _version not in INCLUDED_BOOTSTRAP_VERSION and not links:
        raise ValueError('No include links provided')

    if links:
        return Dependency('bootstrap', version=_version, theme=theme, links=links, dependencies=dependencies)

    _theme = theme if theme else 'vanilla'
    if (_version, _theme) not in _bootstrap_dependencies:
        version_str = ".".join(str(vs) for vs in _version)  # TODO accept str version as parameter
        if _theme not in BOOTSWATCH_THEMES[_version]:
            raise Exception(f'Unsupported theme {_theme} for bootstrap {version_str}')

        _bootstrap_dependencies[(_version, theme)] = BootstrapDependency(
            js_link=_bootstrap_js_links[_version],
            css_link=CSSDependencyLink(
                f'https://cdn.jsdelivr.net/npm/bootswatch@{version_str}/dist/{_theme}/bootstrap.min.css'),
            jquery_dependency=_bootstrap4_jquery_dependency if version_str.startswith('4.') else None,
            version=version, theme=theme)

    return _bootstrap_dependencies[(_version, _theme)]
