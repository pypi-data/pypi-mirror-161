__all__ = ['FormAction', 'FormResponse', 'redirect', 'refresh', 'toast', 'jseval', 'replace_html', 'update_form',
           'update_state', 'error', "success", "warning"]

from dataclasses import dataclass
from collections.abc import Iterable

from wtforms import Form

from elementary_flask.typing import FormActionInit
from .state import form_state


class FormAction:
    def __init__(self, action, **params):
        self.action = action
        self.params = params

    def to_dict(self):
        return {
            "action": self.action,
            "params": self.params,
        }


@dataclass
class FormResponse:
    actions: FormActionInit

    def __post_init__(self):
        if not isinstance(self.actions, Iterable):
            self.actions = [self.actions]

        self.actions = list(update_form(a) if isinstance(a, Form) else a for a in self.actions)

    def to_dict(self):
        return {'actions': [a.to_dict() for a in self.actions]}


def redirect(uri):
    return FormAction('redirect', destination=uri)


def jseval(js_code):
    return FormAction('eval', code=js_code)


def toast(message, message_type='info', message_title=None, sticky=False, timeout=10):
    message_title = message_title if message_title is not None else message_type
    return FormAction('toast', message=message, message_type=message_type, message_title=message_title,
                      sticky=sticky, timeout=timeout)


def replace_html(html):
    return FormAction('replace', html=html)


def update_state(**new_state):
    return FormAction('state', new_state=new_state)


def update_form(form):
    return update_state(formState=form_state(form))


def error(error_msg, message_title="Error", sticky=False, timeout=10):
    return toast(error_msg, message_type='error', message_title=message_title, sticky=sticky, timeout=timeout)


def warning(warning_msg, message_title="Warning", sticky=False, timeout=10):
    return toast(warning_msg, message_type='warning', message_title=message_title, sticky=sticky, timeout=timeout)


def success(success_msg, message_title="Success", sticky=False, timeout=10):
    return toast(success_msg, message_type='success', message_title=message_title, sticky=sticky, timeout=timeout)


def refresh():
    return FormAction('refresh')


def sleep(delay):
    return FormAction('sleep', delay=delay)


# def hide(selector, select_from_document=False, closest=True):
#     return FormAction('hide',
#                       selector=selector, select_from_document=select_from_document, closest=closest
#                       )
