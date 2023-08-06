__all__ = ['form_endpoint_wrapper']

from flask import request

from elementary_flask.globals import current_elementary_flask_app as _app
from .response import FormResponse, error


def form_endpoint_wrapper(frm_cls):
    def _wrap():
        _frm = frm_cls()
        if not _check_referer():
            form_response = error('Error validating this POST Request: Forbidden Referrer.')
        elif not hasattr(_frm, 'validate_on_submit') or _frm.validate_on_submit():
            form_response = _frm.on_submit()
        else:
            # return toast('validation error')
            form_response = [error('Error validating Form'), _frm]

        if not isinstance(form_response, FormResponse):
            form_response = FormResponse(form_response)

        _app.logger.debug('%s submit data: %s, response: %s',
                          frm_cls.__name__, request.form, form_response)
        return form_response.to_dict()

    return _wrap


def _check_referer():
    return True  # TODO
