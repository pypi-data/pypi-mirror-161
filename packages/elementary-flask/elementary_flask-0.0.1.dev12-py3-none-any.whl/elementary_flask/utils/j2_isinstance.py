_CLS_MAPPING = dict()


def _get_cls_mapping():
    if len(_CLS_MAPPING) == 0:
        # init
        from elementary_flask.components import NavigationGroup, NavigationLink, NavigationItem, NavigationSeparator
        _CLS_MAPPING.update(
            {
                # Elementary classes - Navigation
                'NavigationGroup': NavigationGroup,
                'NavigationLink': NavigationLink,
                'NavigationItem': NavigationItem,
                'NavigationSeparator': NavigationSeparator,

                # Built-in Types
                'str': str,
                'bytes': bytes,
                'int': int,
                'float': float,
                'complex': complex,
                'bool': bool,
                'list': list,
                'tuple': tuple,
                'range': range,
                'dict': dict,
                'set': set,
            }
        )

    return _CLS_MAPPING


def j2_isinstance(obj, cls_str):
    return isinstance(obj, _get_cls_mapping().get(cls_str))
