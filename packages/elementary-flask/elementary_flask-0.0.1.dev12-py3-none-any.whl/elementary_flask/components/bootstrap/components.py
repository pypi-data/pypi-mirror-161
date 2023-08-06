from elementary_flask.components import NormalContainer
from elementary_flask.typing import ContainerChildren
from markupsafe import Markup
__all__ = ['BootstrapAlert', 'BootstrapBadge', 'BOOTSTRAP_COLOR_CLASSES']

BOOTSTRAP_COLOR_CLASSES = ('primary', 'secondary', 'success', 'danger', 'warning', 'info', 'light', 'dark')


def _get_color(color, default=None, prefix='text'):
    if color and color in BOOTSTRAP_COLOR_CLASSES:
        pass
    elif default and default in BOOTSTRAP_COLOR_CLASSES:
        color = default
    else:
        color = BOOTSTRAP_COLOR_CLASSES[0]
    return prefix + '-' + color


class BootstrapAlert(NormalContainer):
    default_attributes = {'role': 'alert'}

    def __init__(self, children: ContainerChildren, /, *, color=None, dismissible=True, **kwargs):
        self.classes = "alert" + _get_color(color, prefix='alert')
        if dismissible:
            self.classes += " alert-dismissible fade show"
        children = list(children)
        children.append(Markup("""<button type="button" class="close" data-dismiss="alert" aria-label="Close">"""
                               """<span aria-hidden="true">&times;</span></button>"""))
        super(BootstrapAlert, self).__init__(children, **kwargs)


class BootstrapBadge(NormalContainer):
    html_tag = "span"

    def __init__(self, text, link=False, pill=False, color=None,  **kwargs):
        self.classes = "badge " + _get_color(color, prefix='badge')
        if pill:
            self.classes += " badge-pill"

        if link:
            self.html_tag = 'a'
            # kwargs.setdefault('href', '#')

        super(BootstrapBadge, self).__init__([text], **kwargs)


