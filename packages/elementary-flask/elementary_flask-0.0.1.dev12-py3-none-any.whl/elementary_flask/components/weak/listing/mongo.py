__all__ = ["mongo_collection_listing", "register_mongo_listing"]

from posixpath import join, abspath

from elementary_flask.utils.frozendict import EMPTY_DICT
from .listing import AbstractListing, default_listing_render


# def mongo_collection_admin_listing(
#         cls, *,
#         item_view_uri=None,
#         item_edit_uri=None,
#         item_edit_title=None,
#         item_edit_icon=None,
#         default_renderer=default_listing_render,
#         show_header=True,
#         items_per_page=20,
#         additional_filters=None,
#         additional_actions=None,
#         default_sort=None,
#         id_field='id',
#         listing_fields=None,
#         view_fields=None,
#         edit_fields=None,
#         filters_fields=None,
#
# ):
#     name = cls.__name__ + 'MongoCollection'
#     cls_fields = [k for k, v in cls._fields.items() if k != 'id']
#     view_fields = view_fields or cls_fields
#     edit_fields = edit_fields or cls_fields
#
#     def list_items(self, page=1, items_per_page=20, filters=None, query=None, sort=None):
#         if sort:
#             return self._mongo_document_cls.objects(
#                 **_mfilter(filters=filters, query=query)
#             ).order_by(*_msort(sort))[(page - 1) * items_per_page:page * items_per_page]
#         return self._mongo_document_cls.objects(
#             **_mfilter(filters=filters, query=query)
#         )[(page - 1) * items_per_page:page * items_per_page]
#
#     def count_items(self, filters=None, query=None):
#         return self._mongo_document_cls.objects(**_mfilter(filters=filters, query=query)).count()
#
#     cls_dict = dict(
#         _mongo_document_cls=cls,
#         list_items=list_items,
#         count_items=count_items,
#         columns=listing_fields,
#         id_field=id_field,
#         item_view_uri=item_view_uri,
#         item_edit_uri=item_edit_uri,
#         item_edit_title=item_edit_title,
#         item_edit_icon=item_edit_icon,
#         default_renderer=default_renderer,
#         show_header=show_header,
#         items_per_page=items_per_page,
#         default_sort=default_sort,
#     )
#     # TODO delete action
#     # cls_dict.update(actions)
#     # cls_dict.update(filters)
#
#     return type(
#         name,
#         (AbstractListing,),
#         cls_dict
#     )


def mongo_collection_listing(
        document_cls, *,
        item_view_uri='./{}',
        item_view_title=None,
        item_view_icon="fas fa-eye",  # TODO generic icon
        item_edit_uri="./{}/edit",
        item_edit_title=None,
        item_edit_icon="fas fa-pen",  # TODO generic icon
        item_delete_func=None,
        item_delete_title=None,
        item_delete_icon="fas fa-trash",  # TODO: generic icon
        default_renderer=default_listing_render,
        show_header=True,
        items_per_page=20,
        additional_filters=None,
        additional_actions=None,
        default_sort=None,
        id_field='id',
        listing_fields=None,
        view_fields=None,
        edit_fields=None,
        filters_fields=None,
        click_action='view',
        generate_edit_form=True,
        edit_form=None,
        filter_parser=None,
        sort_parser=None

):
    cls_fields = [k for k, v in document_cls._fields.items() if k != 'id']
    listing_fields = listing_fields or cls_fields
    view_fields = view_fields or cls_fields
    edit_fields = edit_fields or cls_fields

    filter_parser = filter_parser or _mfilter
    sort_parser = sort_parser or _msort

    # edit form
    if edit_form is None and generate_edit_form:
        edit_form = _generate_edit_form(document_cls)

    class _CLS(AbstractListing):
        _mongo_document_cls = document_cls
        _mongo_filter_parser = staticmethod(filter_parser)
        _mongo_sort_parser = staticmethod(sort_parser)

        def list_items(self, page=1, items_per_page=20, filters=None, query=None, sort=None):
            item_count = self.count_items(filters=None, query=None)
            # if item_count == 0:
            #     return []
            cursor = self._mongo_document_cls.objects(self._mongo_filter_parser(filters=filters, query=query))
            if sort:
                cursor = cursor.order_by(*self._mongo_sort_parser(sort))
            slice_start = (page - 1) * items_per_page
            slice_end = page * items_per_page
            return cursor[slice_start:slice_end]

        def count_items(self, filters=None, query=None):
            return self._mongo_document_cls.objects(self._mongo_filter_parser(filters=filters, query=query)).count()

        def delete(self, ids):
            from elementary_flask.form import toast
            docs = list(self._mongo_document_cls.objects(**{self.id_field + '__in': ids}))
            for d in docs:
                d.delete()
            if len(docs) > 1 or len(docs) == 0:
                return toast("%d item are delete" % len(docs), message_type="success")  # TODO refresh items
            if len(docs) == 1:
                return toast("item is deleted", message_type="success")  # TODO refresh items

    _CLS.__name__ = document_cls.__name__ + 'MongoListing'

    cls_dict = dict(
        columns=listing_fields,
        id_field=id_field,
        item_view_uri=item_view_uri,
        item_view_title=item_view_title,
        item_view_icon=item_view_icon,
        item_edit_uri=item_edit_uri,
        item_edit_title=item_edit_title,
        item_edit_icon=item_edit_icon,
        item_delete_func=item_delete_func or _CLS.delete,
        item_delete_title=item_delete_title,
        item_delete_icon=item_delete_icon,
        default_renderer=default_renderer,
        show_header=show_header,
        items_per_page=items_per_page,
        default_sort=default_sort,
        click_action=click_action,
        edit_form=edit_form,
        endpoint_functions=None
    )

    # additional actions & filters
    if additional_actions:
        for a in additional_actions:
            cls_dict['additional_action_' + a.name] = a
    if additional_filters:
        for f in additional_filters:
            cls_dict['additional_filter_' + f.name] = f

    for k, v in cls_dict.items():
        setattr(_CLS, k, v)
    # _CLS.__dict__.update()
    # TODO delete action
    # cls_dict.update(actions)
    # cls_dict.update(filters)

    return _CLS


def register_mongo_listing(
        bp, cls, listing_rule, /,
        page_layout='default',
        navigation=False,
        navigation_title=None,
        navigation_params=None,
        navigation_icon=None,
        list_page_options=EMPTY_DICT,
        listing_options=EMPTY_DICT,
        view_page_layout='default',
        view_page_options=EMPTY_DICT,
        view_page_rule=None,
        create_page_layout='default',
        create_page_options=EMPTY_DICT,
        create_page_rule=None,

):
    # Listing
    cls = bp.listing(**listing_options)(cls)
    cls.endpoint_functions = generate_endpoint_functions(cls)

    # List page
    bp.route_page(listing_rule,
                  page_layout=page_layout,
                  navigation=navigation,
                  navigation_title=navigation_title,
                  navigation_params=navigation_params,
                  navigation_icon=navigation_icon,
                  **list_page_options)(cls.endpoint_functions['list'])

    # View page
    if cls.item_view_uri is not None:
        if view_page_rule is None:
            view_page_rule = abspath(join(listing_rule, cls.item_view_uri)).format('<doc_id>')
        bp.route_page(view_page_rule,
                      page_layout=view_page_layout,
                      **create_page_options)(cls.endpoint_functions['view'])

    # TODO: create & edit forms + on_submit functions + pages
    # if cls.edit_form is not None:
    #     # Create Form
    #     cls.edit_form = bp.form()(cls.edit_form)
    #
    #     # Create Page
    #     if create_page_rule is None:
    #         create_page_rule = abspath(join(listing_rule, 'create'))
    #     bp.route_page(create_page_rule,
    #                   page_layout=create_page_layout,
    #                   **view_page_options)(cls.endpoint_functions['create'])
    return cls


def _msort(sort=None):
    if not sort:
        return list()
    ret = list()
    for k, o in sort:
        ret.append(f'{"-" if o == "desc" else "+"}{k}')
    return ret


def _mfilter(filters=None, query=None):
    from mongoengine.queryset.visitor import Q

    # TODO query and filters
    return Q()


def _generate_edit_form(document_cls):
    from flask_mongoengine.wtf import model_form
    ret = model_form(document_cls)
    ret.__name__ = document_cls.__name__ + 'EditForm'
    return ret


def generate_endpoint_functions(cls):
    def list_function():
        return cls()

    def view_function(doc_id):
        obj = cls._mongo_document_cls.objects(**{cls.id_field: doc_id}).first()
        if obj:
            return str(dict(obj.to_mongo()))
        return 404

    list_function.__name__ = cls.__name__ + 'List'
    view_function.__name__ = cls.__name__ + 'View'
    ret = dict(list=list_function, view=view_function)

    if cls.edit_form:

        def create_function():
            return cls.edit_form()

        def edit_function(doc_id):
            obj = cls._mongo_document_cls.objects(**{cls.id_field: doc_id}).first()
            if obj:
                return cls.edit_form(**dict(obj.to_mongo()))
            return 404

        create_function.__name__ = cls.__name__ + 'Create'
        edit_function.__name__ = cls.__name__ + 'Edit'
        ret['create'] = create_function
        ret['edit'] = edit_function

    return ret
