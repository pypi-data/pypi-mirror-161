__all__ = ['form_state', 'form_json_state']
import json

from flask import url_for


def form_json_state(form):
    state = form_state(form)
    state['data'] = {k: f._value() if hasattr(f, '_value') else f.data for k, f in form._fields.items()}
    return json.dumps(state)


def form_state(form):
    errors = dict()
    for k in list(form.data.keys()) + [None]:
        errors[k or ''] = '; '.join(form.errors.get(k, []))

    return dict(
        id=form.elementary_flask_form_id,
        method='POST',
        uri=url_for(form.elementary_flask_action_endpoint()),
        data=form.data,
        errors=errors,

    )
