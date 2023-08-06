from collections.abc import Mapping
from functools import wraps
from typing import Optional, List, Any, Callable

from box import Box


def chunks(lst: List, n: int):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def boxify(use_snakes: Optional[bool] = False,
           default_box_attr: Optional[Any] = object(),
           default_box: Optional[bool] = False) -> Callable:
    """
    Convenience decorator to convert a returned dictionary into a Box object for ease of use.

    :param use_snakes: Convert camelCase into snake_case.
    :param default_box_attr: Set default attribute to return.
    :param default_box: Behave like a recursive default dict.
    :return: Box object if original return was a Mapping (dictionary).
    """

    def _boxify(func):
        @wraps(func)
        def _impl(self, *args, **kwargs) -> Optional[Box]:
            dict_ = func(self, *args, **kwargs)
            if dict_ and isinstance(dict_, Mapping):
                return Box(
                    dict_,
                    camel_killer_box=use_snakes,
                    default_box_attr=default_box_attr,
                    default_box=default_box
                )
            return dict_

        return _impl

    return _boxify
