from __future__ import annotations

import warnings
from functools import wraps
from typing import Callable


def deprecated(reason: str, since: str, removed: str | None = None, silent: bool = False):
    """Wrapper used to warn about deprecated functionality in Datify.

    :param reason: the reason of the deprecation
    :param since: the version in which the function was deprecated
    :param removed: the version in which the function is due to being removed
    :param silent: whether to suppress warnings about deprecation or not
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if silent:
                return func(*args, **kwargs)

            warnings.warn(
                f'The `{func.__name__}` is deprecated since {since} ({reason}) and will be removed in '
                + (removed if removed else
                   'future release') + '. Consider not to use it.',
                category=DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        return wrapper

    return decorator
