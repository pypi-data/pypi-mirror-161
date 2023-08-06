class FrozenDict(dict):
    r"""
    A simple immutable dictionary.
    """

    def __setitem__(self, key, val, *args, **kwargs):
        raise TypeError(
            f"'{self.__class__.__name__}' object doesn't support item "
            "assignment"
        )

    def __delitem__(self, key, *args, **kwargs):
        raise TypeError(
            f"'{self.__class__.__name__}' object doesn't support item "
            "deletion"
        )


EMPTY_DICT = FrozenDict()
