from typing import Callable
import functools
from numpy import not_equal
from pandas import Series


def treatment_foo(foo):
    """
    Convinience class to make help make treatmen functions
    """
    @functools.wraps(foo)
    def wrapper(x, y, *args, **kwargs):
        assert isinstance(x, Series) and isinstance(y, Series)
        _ret = y.to_frame('control').join(x.to_frame('passed'), rsuffix='_', how='left')
        ret = foo(y=_ret.iloc[:, 0], x=_ret.iloc[:, 1], *args, **kwargs)
        if not isinstance(ret, (Series, int, float, str)):
            raise TypeError(f'{foo} must return Series or scalar, but returned {ret}')
        if ret.max():
            return _ret[ret]
    return wrapper


@treatment_foo
def ne(x, y):
    return not_equal(x, y)


@treatment_foo
def not_match(x, y):
    return x != y


@treatment_foo
def low_diff(y, x):
    diff = x/y
    return (diff < 0.5) | (diff > 2)


@treatment_foo
def high_diff(y, x):
    diff = x/y
    return (diff < 0.1) | (diff > 10)