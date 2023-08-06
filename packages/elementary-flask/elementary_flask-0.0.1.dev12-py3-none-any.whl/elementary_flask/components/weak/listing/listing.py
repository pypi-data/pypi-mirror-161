__all__ = ['AbstractListing']

from abc import ABC, abstractmethod

from flask import request
from flask_wtf import FlaskForm
from werkzeug.datastructures import ImmutableMultiDict, CombinedMultiDict, ImmutableDict

from elementary_flask.typing import FormResponseReturn
from ._page_uri import page_uri
from .action import ListingAction
from .column import ListingColumn
from .filter import ListingFilter, get_parsed_filters
from .sort import get_parsed_sort
from .renderer import default_listing_render
from ..form import error, redirect
from ... import AbstractWeakComponent

SUBMIT_METHODS = ("POST", "PUT", "PATCH", "DELETE")


class AbstractListing(AbstractWeakComponent, ABC):
    columns = None
    id_field = None
    item_view_uri = None
    item_view_title = None
    item_view_icon = None  # TODO: generic icon
    item_edit_uri = None
    item_edit_title = None
    item_edit_icon = None  # TODO: generic icon
    item_delete_func = None
    item_delete_title = None
    item_delete_icon = None  # TODO: generic icon
    _actions = None
    _columns = None
    _filters = None
    _init = False
    default_renderer = default_listing_render
    show_header = True
    items_per_page = 20
    default_sort = None
    click_action = 'view'

    def __init__(self):
        super(AbstractListing, self).__init__()
        self.view_page_kwargs = None
        self.view_form = FlaskForm()

    def list_items_request(self):
        def _correct_page(p, mp):
            if p > mp:
                p = mp
            if p < 1:
                p = 1
            return p

        try:
            page = request.args.get('page', 1, type=int)
        except:
            page = 1
        items_per_page = self.items_per_page
        filters = request.args.get('filters', None)
        query = request.args.get('query', None)
        sort = request.args.get('sort', None)
        c_total = self.count_items(filters=get_parsed_filters(), query=query)
        max_page = (c_total // items_per_page) + (1 if c_total % items_per_page else 0)
        page = _correct_page(page, max_page)
        if c_total > 0:
            c_f = (page - 1) * items_per_page + 1
            c_t = min(page * items_per_page, c_total)
            count_str = f"{c_f}-{c_t}/{c_total}"
        else:
            count_str = ""

        next_page = page_uri(page=_correct_page(page + 1, max_page), filters=filters, query=query, sort=sort)
        previous_page = page_uri(page=_correct_page(page - 1, max_page), filters=filters, query=query, sort=sort)
        return self.list_items(
            page=page, items_per_page=items_per_page, filters=get_parsed_filters(),
            query=query, sort=get_parsed_sort(self.default_sort)), count_str, next_page, previous_page

    @abstractmethod
    def list_items(self, page=1, items_per_page=20, filters=None, query=None, sort=None):
        raise NotImplementedError()

    @abstractmethod
    def count_items(self, filters=None, query=None):
        raise NotImplementedError()

    def __len__(self):
        return self.count_items()

    @classmethod
    def init_listing_cls(cls):
        if not cls._init:
            actions = dict()
            columns = dict()
            filters = list()

            if cls.columns is not None:
                for column_or_name in cls.columns:
                    if isinstance(column_or_name, ListingColumn):
                        columns[column_or_name.name] = column_or_name
                    else:
                        columns[column_or_name] = ListingColumn(column_or_name)

            for key in dir(cls):
                itm = getattr(cls, key)
                # if getattr(itm, 'elementary_flask_listing_action', False) and callable(itm):
                if isinstance(itm, ListingAction):
                    actions[itm.name] = itm
                elif isinstance(itm, ListingColumn):
                    columns[itm.name] = itm
                elif isinstance(itm, ListingFilter):
                    filters.append(itm)
            # view action
            if 'view' not in actions and cls.item_view_uri:
                actions['view'] = ListingAction(lambda s, id_: redirect(cls.item_view_uri.format(id_)),
                                                name='view', hidden=False,
                                                icon=cls.item_view_icon, title=cls.item_view_title)
            # edit action
            if 'edit' not in actions and cls.item_edit_uri:
                actions['edit'] = ListingAction(lambda s, id_: redirect(cls.item_edit_uri.format(id_)),
                                                name='edit',
                                                icon=cls.item_edit_icon,
                                                title=cls.item_edit_title,
                                                )
            # delete action
            if 'delete' not in actions and cls.item_delete_func:
                actions['delete'] = ListingAction(cls.item_delete_func,
                                                  name='delete',
                                                  icon=cls.item_delete_icon,
                                                  title=cls.item_delete_title,
                                                  batch=True,
                                                  )

            cls._actions = ImmutableDict(actions)
            filters.sort(key=lambda x: x.order)
            cls._filters = filters
            # cls._filters = ImmutableDict({f.name: f for f in filters})

            # columns = dict()

            cls._columns = tuple(sorted(columns.values(), key=lambda x: x.order))
            cls._init = True

    def on_submit(self) -> FormResponseReturn:
        # if self._actions is None:
        self.init_listing_cls()
        formdata, action_name, ids = _get_form_data_splits()

        if ids is None:
            return error('No item ID was sent!')

        if action_name is None or action_name not in self._actions:
            return error('Unknown action was sent!')

        action = self._actions.get(action_name)
        # action = action_func.elementary_flask_listing_action

        if not (action.batch or len(ids) == 1) or not (action.form_cls is None or formdata):
            return error('Error processing action data!')

        # ids = [ids] if isinstance(ids, str) and action.batch else ids
        ids = ids[0] if not action.batch else ids
        # if action.form_cls: # TODO modal form support
        #     return action(ids, action.form_cls(formdata=formdata))
        return action(self, ids)

    @classmethod
    def page_view(cls, **kwargs):
        return cls()(**kwargs)

    def hidden_thead(self):
        return "" if self.show_header else "hidden"

    def listing_id(self):
        return self.__class__.__name__ + '.' + str(hash(self))

    @classmethod
    def form_action(cls):
        return '/listing'

    # @classmethod
    # def field_title(cls, field_name):
    #     if not hasattr(cls, field_name + '_field_title'):
    #         setattr(cls, field_name + '_field_title', field_name)
    #     return getattr(cls, field_name + '_field_title')
    #
    # @classmethod
    # def field_generator(cls, field_name):
    #     def _generator(itm):
    #         return getattr(itm, field_name, None)
    #
    #     if not hasattr(cls, field_name + '_generator'):
    #         setattr(cls, field_name + '_generator', _generator)
    #     return getattr(cls, field_name + '_generator')
    #
    # @classmethod
    # def field_formatter(cls, field_name):
    #     def _formatter(val):
    #         return html_escape(val)
    #
    #     if not hasattr(cls, field_name + '_formatter'):
    #         setattr(cls, field_name + '_formatter', _formatter)
    #     return getattr(cls, field_name + '_formatter')
    #
    # @classmethod
    # def field_html_generator(cls, field_name):
    #     def _html_generator(itm):
    #         return cls.field_formatter(field_name)(cls.field_generator(field_name)(itm))
    #
    #     if not hasattr(cls, field_name + '_html_generator'):
    #         setattr(cls, field_name + '_html_generator', _html_generator)
    #     return getattr(cls, field_name + '_html_generator')


def _get_form_data_splits():
    if _is_submitted():
        if request.files:
            return _split_form_data(CombinedMultiDict((request.files, request.form)))
        elif request.form:
            return _split_form_data(request.form)
        elif request.get_json():
            return _split_form_data(ImmutableMultiDict(request.get_json()))

    return None, None


def _split_form_data(obj):
    # ret = dict(**obj)
    obj = obj.copy()
    action = obj.pop('action', None)
    ids = obj.poplist("ids")
    # _app.logger.debug(repr(ids))
    return ImmutableMultiDict(obj), action, ids


def _is_submitted():
    return bool(request) and request.method in SUBMIT_METHODS
