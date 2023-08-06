from enum import Enum
from .response import FormAction
from elementary_flask.typing import Union, Iterable

__all__ = ['SelectorTypeEnum', 'DOMManipulationTarget', 'DOMManipulationActionType', 'DOMManipulationActionType',
           'DOMManipulation', 'manipulate_dom_element', 'MANIPULATIONS', 'DOMManipulationFormAction',
           'hide', 'enable', 'disable', 'set_class', 'insert'
           ]


class SelectorTypeEnum(str, Enum):
    BY_ID = "by_id"
    BY_CLASS = "by_class"
    QUERY_SELECTOR = "query_selector"
    CLOSEST = "closest"


class DOMManipulationTarget(str, Enum):
    CLASS = "class"
    ATTRIBUTES = "attributes"
    STYLES = "styles"
    SELF = "self"
    PARENT = "parent"
    DOCUMENT = "document"


class DOMManipulationActionType(str, Enum):
    EXTEND = "extend"
    UPDATE = "update"
    REMOVE = "remove"
    CLEAR = "clear"
    AFFECT = "affect"
    REPLACE = "replace"
    INSERT = "insert"


class DOMManipulation:

    def __init__(
            self,
            target: DOMManipulationTarget,
            action_type: DOMManipulationActionType,
            *args
    ):
        self.target = target
        self.action_type = action_type
        self.args = args

    def to_dict(self):
        return {
            'target': self.target,
            'action_type': self.action_type,
            'args': self.args
        }

    def copy(self, *args):
        return DOMManipulation(self.target, self.action_type, *args)


class DOMManipulationFormAction(FormAction):
    def __init__(self, /, *,
                 selector: str,
                 manipulations: Union[DOMManipulation, Iterable[DOMManipulation]],
                 selector_type: SelectorTypeEnum = SelectorTypeEnum.BY_ID,
                 select_from_document=False,
                 # manipulate_all=True,
                 ):
        manipulations = [manipulations] if isinstance(manipulations, DOMManipulation) else manipulations
        super(DOMManipulationFormAction, self).__init__(
            'dom_element_manipulation',
            selector_type=selector_type,
            selector=selector,
            manipulations=[m.to_dict() for m in manipulations],
            select_from_document=select_from_document,
            # manipulate_all=manipulate_all,
        )


manipulate_dom_element = DOMManipulationActionType


class MANIPULATIONS:
    HIDE = DOMManipulation(DOMManipulationTarget.STYLES, DOMManipulationActionType.UPDATE, {'display': 'none'})
    DISABLE = DOMManipulation(DOMManipulationTarget.SELF, DOMManipulationActionType.UPDATE, {'disabled': True})
    ENABLE = DOMManipulation(DOMManipulationTarget.SELF, DOMManipulationActionType.UPDATE, {'disabled': False})
    SELF_UPDATE = DOMManipulation(DOMManipulationTarget.SELF, DOMManipulationActionType.UPDATE)


def hide(selector, select_from_document=False, selector_type=SelectorTypeEnum.BY_ID):
    return DOMManipulationFormAction(selector=selector,
                                     manipulations=MANIPULATIONS.HIDE,
                                     select_from_document=select_from_document,
                                     selector_type=selector_type)


def enable(selector, select_from_document=False, selector_type=SelectorTypeEnum.BY_ID):
    return DOMManipulationFormAction(selector=selector,
                                     manipulations=MANIPULATIONS.ENABLE,
                                     select_from_document=select_from_document,
                                     selector_type=selector_type)


def disable(selector, select_from_document=False, selector_type=SelectorTypeEnum.BY_ID):
    return DOMManipulationFormAction(selector=selector,
                                     manipulations=MANIPULATIONS.DISABLE,
                                     select_from_document=select_from_document,
                                     selector_type=selector_type)


def set_class(selector, element_class, select_from_document=False, selector_type=SelectorTypeEnum.BY_ID):
    return DOMManipulationFormAction(selector=selector,
                                     manipulations=MANIPULATIONS.SELF_UPDATE.copy({'className': element_class}),
                                     select_from_document=select_from_document,
                                     selector_type=selector_type)


def insert(selector, html_code, position="afterend", parent=False, hide_element=False,
           select_from_document=False, selector_type=SelectorTypeEnum.BY_ID):
    manipulations = [
        DOMManipulation(
            DOMManipulationTarget.PARENT if parent else DOMManipulationTarget.SELF,
            DOMManipulationActionType.INSERT,
            position,
            html_code,
        )
    ]
    if hide_element:
        manipulations.insert(0, MANIPULATIONS.HIDE)
    return DOMManipulationFormAction(selector=selector,
                                     manipulations=manipulations,
                                     select_from_document=select_from_document,
                                     selector_type=selector_type)
