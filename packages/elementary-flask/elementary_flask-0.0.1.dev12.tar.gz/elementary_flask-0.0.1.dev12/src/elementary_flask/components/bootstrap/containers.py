from elementary_flask.components import NormalContainer
from elementary_flask.typing import ContainerChildren
__all__ = ['RESPONSIVE_CONTAINER_BREAKPOINTS', 'Row', 'Col', 'ResponsiveContainer']

RESPONSIVE_CONTAINER_BREAKPOINTS = ('fluid', 'sm', 'md', 'lg', 'xl', 'xxl')


class Row(NormalContainer):
    classes = 'row'


class Col(NormalContainer):
    classes = 'col'


class ResponsiveContainer(NormalContainer):
    def __init__(self, children: ContainerChildren, /, *, container_breakpoint=None, **kwargs):
        if container_breakpoint is None or container_breakpoint not in RESPONSIVE_CONTAINER_BREAKPOINTS:
            container_breakpoint = ''
        else:
            container_breakpoint = '-' + container_breakpoint
        self.classes = 'container' + container_breakpoint
        super(ResponsiveContainer, self).__init__(children, **kwargs)
