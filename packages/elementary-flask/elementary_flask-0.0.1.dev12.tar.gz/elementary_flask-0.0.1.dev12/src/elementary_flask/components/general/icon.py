__all__ = ['IconMixin', 'HTMLIcon', 'IClassIcon', 'get_icon']

from elementary_flask.typing import RenderReturnValue
from .. import AbstractHTMLElementComponent


class IconMixin:
    pass
    # def __init__(self, icon_class=None):
    #     super(AbstractIcon, self).__init__()
    #     self.icon_class = icon_class


class HTMLIcon(IconMixin):
    def __init__(self, html_code):
        self.html_code = html_code

    def render(self, **options) -> RenderReturnValue:
        return self.html_code


class IClassIcon(AbstractHTMLElementComponent, IconMixin):
    html_tag = 'i'

    def __init__(self, icon_classes, **attributes):
        super(IClassIcon, self).__init__(extra_classes=icon_classes, **attributes)


def get_icon(icn):
    return _get_icon(icn)


def _get_icon(icn, check_mappings=True):
    if isinstance(icn, IconMixin):
        return icn
    if icn and isinstance(icn, str):
        if check_mappings:
            for icn_mapping in (_DEFAULT_ICON_MAPPING,):  # TODO app icon map & theme icon map
                if icn in icn_mapping:
                    return _get_icon(icn_mapping[icn], check_mappings=False)

        return IClassIcon(icn)
    return None


_DEFAULT_ICON_MAPPING = {

}
