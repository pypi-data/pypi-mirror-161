__all__ = ['AbstractHTMLElementComponent', 'append_classes', 'HTMLElementComponent']

from abc import ABC

from wtforms.widgets.core import html_params  # noqa
from markupsafe import Markup

from .component import AbstractComponent, render
from elementary_flask.typing import RenderReturnValue


class AbstractHTMLElementComponent(AbstractComponent, ABC):
    html_params = staticmethod(html_params)
    void_element = False
    html_tag = "div"
    classes = None
    default_attributes = None

    def __init__(self, extra_classes=None, attributes=None, **extra_attributes):
        self.base_attributes = dict()
        if self.default_attributes:
            self.base_attributes = dict(self.default_attributes)
        if attributes:
            self.base_attributes.update(attributes)
        self.base_attributes.update(extra_attributes)

        if self.classes or extra_classes:
            self.base_attributes['class'] = append_classes(
                self.base_attributes.get('class', None),
                self.classes,
                extra_classes)

    def render_start(self, extra_classes=None, attributes=None, **extra_attributes) -> RenderReturnValue:
        _attributes = dict(self.base_attributes)
        _attributes.update(attributes or dict())
        _attributes.update(extra_attributes)
        if extra_classes:
            _attributes['class'] = append_classes(_attributes.get('class', None), extra_classes)
        return Markup("<%s %s>" % (self.html_tag, self.html_params(**_attributes)))

    def render_end(self, /, **options) -> RenderReturnValue:
        return Markup('</%s>' % self.html_tag)

    def render(self, /, extra_classes=None, tag_attributes=None, **options) -> RenderReturnValue:
        tag_attributes = tag_attributes or dict()
        if self.void_element:
            return self.render_start(extra_classes=extra_classes, **tag_attributes)

        return (
                self.render_start(extra_classes=extra_classes, **tag_attributes)
                + self.render_inner_html() + self.render_end()
        )

    def render_inner_html(self, **options) -> RenderReturnValue:
        return ""


def append_classes(*classes_strings):
    ret = [c.strip() for c in classes_strings if c and c.strip()]
    if ret:
        return ' '.join(ret)
    return None


class HTMLElementComponent(AbstractHTMLElementComponent):
    def __init__(self, html_tag, inner_component=None, void_element=False, classes=None, attributes=None):
        self.html_tag = html_tag
        self.void_element = void_element
        self.classes = classes
        self.inner_component = inner_component
        super(HTMLElementComponent, self).__init__(attributes=attributes)

    def render_inner_html(self, **options) -> RenderReturnValue:
        if self.inner_component:
            return render(self.inner_component)
        return ''
