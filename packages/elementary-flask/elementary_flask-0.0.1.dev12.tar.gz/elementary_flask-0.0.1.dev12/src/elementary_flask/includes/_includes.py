from dataclasses import dataclass, field
from html import escape as html_escape
from typing import Iterable

from elementary_flask.typing import OptionalSet, Union, List, Optional

REDUCE_INCLUDES_MAX_DEPTH = 5


@dataclass()
class DependencyLink:
    link: str
    include_type: str
    include_position: Optional[str] = None
    cross_origin: Optional[str] = 'anonymous'
    integrity: Optional[str] = None
    defer: bool = False

    def __post_init__(self):
        if self.include_type not in ('css', 'javascript'):
            raise ValueError('unsupported include type: ' + self.include_type)
        if self.include_type == 'css':
            self.include_position = 'head'
        if self.include_position not in (None, 'body', 'head'):
            self.include_position = None
        if self.include_position is None:
            self.include_position = 'body' if self.include_type == 'javascript' else 'head'

    def render_dependency_link(self):
        params = ''
        if self.cross_origin:
            params += f'crossorigin="{html_escape(self.cross_origin)}"'
        if self.integrity:
            params += f' integrity="{html_escape(self.integrity)}"'

        if self.include_type == 'css':
            return f'<link href="{self.link}" rel="stylesheet" {params}>'
        else:
            return f'<script {"defer" if self.defer else ""} src="{self.link}"  {params}></script>'


@dataclass()
class Dependency:
    name: str
    version: Union[tuple[int], str] = None
    theme: Optional[str] = None
    links: List[DependencyLink] = field(default_factory=list)
    css_includes: OptionalSet = None
    js_includes: OptionalSet = None
    dependencies: Optional[List["Dependency"]] = field(default_factory=list)

    def __post_init__(self):
        if isinstance(self.version, str):
            self.version = parse_str_version(self.version)

        create_dependency_links(self.links, css_includes=self.css_includes, js_includes=self.js_includes)
        self.css_includes, self.js_includes = None, None

    def __add__(self, other):
        if self == other:
            return self

        assert self.name == other.name

        # version compatibility and priority
        version_prior = _compare_version(self.version, other.version)

        # theme compatibility and priority
        theme_prior = _compare_theme(self.theme, other.theme)

        if version_prior == theme_prior or (theme_prior == self and not self.theme):
            return version_prior
        raise IncludeVersionThemeIncompatibility()

    def flatten(self):
        return self._flatten()

    def _flatten(self, processed=None):
        processed = processed if processed is not None else list()
        if self in processed:
            return processed

        for d in self.dependencies:
            if d not in processed:
                d._flatten(processed=processed)

        processed.append(self)

        return processed


@dataclass()
class ComponentIncludes:
    dependencies: List[Dependency] = field(default_factory=list)
    css_includes: OptionalSet = field(default_factory=set)
    js_includes: OptionalSet = field(default_factory=set)

    def __post_init__(self):
        if self.css_includes:
            for css_link in self.css_includes:
                self.dependencies.append(Dependency(css_link, css_includes={css_link}))
            self.css_includes = None
        if self.js_includes:
            for js_link in self.js_includes:
                self.dependencies.append(Dependency(js_link, js_includes={js_link}))
            self.js_includes = None

    def __add__(self, other):
        if other is None:
            return self

        union_dependencies = merge_dependencies(self.dependencies + other.dependencies)

        return ComponentIncludes(list(union_dependencies))

    def render_head_includes(self) -> str:
        return self._render_position('head')

    def render_body_includes(self) -> str:
        return self._render_position('body')

    def _render_position(self, position):
        return ''.join(link.render_dependency_link() for dep in self.dependencies for link in dep.links
                       if link.include_position == position)


class CSSDependencyLink(DependencyLink):
    def __init__(self,
                 link: str,
                 include_position: Optional[str] = None,
                 cross_origin: Optional[str] = 'anonymous',
                 integrity: Optional[str] = None,
                 ):
        super(CSSDependencyLink, self).__init__(link, 'css', include_position=include_position,
                                                cross_origin=cross_origin, integrity=integrity)


class JavascriptDependencyLink(DependencyLink):
    def __init__(self,
                 link: str,
                 include_position: Optional[str] = None,
                 cross_origin: Optional[str] = 'anonymous',
                 integrity: Optional[str] = None,
                 defer=False,
                 ):
        super(JavascriptDependencyLink, self).__init__(link, 'javascript', include_position=include_position,
                                                       cross_origin=cross_origin, integrity=integrity, defer=defer)


class BootstrapDependency(Dependency):
    def __init__(self,
                 js_link: Union[DependencyLink, str],
                 css_link: Union[DependencyLink, str],
                 version: Union[tuple[int], str] = None,
                 theme: Optional[str] = None,
                 jquery_dependency: Union[str, Dependency] = None,
                 other_links: Optional[List[DependencyLink]] = None,
                 ):
        # JQuery Dependency
        dependencies = list()
        if jquery_dependency:
            if isinstance(jquery_dependency, Dependency):
                dependencies.append(jquery_dependency)
            else:
                dependencies.append(Dependency('jquery', links=[JavascriptDependencyLink(
                    'https://cdn.jsdelivr.net/npm/jquery@3.5.1/dist/jquery.slim.min.js')]))

        # CSS & Javascript
        links = list()
        links.append(js_link if isinstance(js_link, DependencyLink) else JavascriptDependencyLink(js_link))
        links.append(css_link if isinstance(css_link, DependencyLink) else CSSDependencyLink(js_link))
        if other_links:
            links.extend(other_links)

        super(BootstrapDependency, self).__init__('bootstrap', version=version, theme=theme, dependencies=dependencies,
                                                  links=links)


class IncludeVersionIncompatibility(Exception):
    pass


class IncludeThemeIncompatibility(Exception):
    pass


class IncludeVersionThemeIncompatibility(Exception):
    pass


def merge_dependencies(dependencies):
    union_dependencies = {}
    for main_dependency in dependencies:
        for d in main_dependency.flatten():
            if d.name in union_dependencies:
                union_dependencies[d.name] += d
            else:
                union_dependencies[d.name] = d
    return list(union_dependencies.values())


def parse_str_version(v: str):
    try:
        return tuple(int(t) for t in v.split('.'))
    except:
        return v


def format_str_version(v):
    return ".".join(str(vs) for vs in v)


def create_dependency_links(links, css_includes=None, js_includes=None):
    if css_includes:
        for css_link in css_includes:
            links.append(DependencyLink(css_link, 'css'))
    if js_includes:
        for js_link in js_includes:
            links.append(DependencyLink(js_link, 'javascript'))


def _compare_version(v1, v2):
    if v1 == v2:
        return v1
    if not (isinstance(v1, tuple) and isinstance(v2, tuple)):
        raise IncludeVersionIncompatibility()

    if not v2:
        return v1
    elif not v1:
        return v2
    elif v1 and v2 and v1[0] != v2[0]:
        raise IncludeVersionIncompatibility()
    elif len(v1) == len(v2):
        return v1 if v1 >= v2 else v2
    else:
        return (v1[0],) + _compare_version(v1[1:], v2[1:])


def _compare_theme(t1, t2):
    if t1 == t2 or not t2:
        return t1
    elif not t1:
        return t2
    else:
        raise IncludeThemeIncompatibility()


def reduce_includes(*includes_or_components) -> ComponentIncludes:
    def _reduce_includes(*args, depth=0) -> Optional[ComponentIncludes]:
        ret = None
        for itm in args:
            if isinstance(itm, Iterable) and depth < REDUCE_INCLUDES_MAX_DEPTH:
                itm = _reduce_includes(*itm, depth=depth + 1)
            elif isinstance(itm, Iterable):
                ValueError('includes max depth reached')

            if itm is None:
                continue


            if isinstance(itm, ComponentIncludes):
                if ret is None:
                    ret = itm
                else:
                    ret += itm

        return ret

    reduced = _reduce_includes(*includes_or_components)
    if reduced is None:
        return ComponentIncludes()
    return reduced
