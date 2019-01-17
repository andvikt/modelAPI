from logging import getLogger, ERROR, WARNING
from typing import Callable
from pandas import DataFrame, Series, concat

RAISE = False
VAL_LOGGER = getLogger('data.validation')
LEVELS = {
    ERROR: 'error'
    , WARNING: 'warning'
}


def set_val_raise(val: bool):
    global RAISE
    RAISE = val


def if_true(x, foo:Callable, action:Callable):
    if foo(x):
        action(x)
    return x


def raise_error(cvalue, cname, pass_name, pass_value):
    raise Exception(f'{cname} did not pass {pass_name} with value {cvalue}, pass_value {pass_value}')


def warn(cvalue, cname, pass_name, pass_value):
    VAL_LOGGER.warning(f'{cname} did not pass {pass_name} with value {cvalue}, pass_value {pass_value}')


class _LoggerMixin(object):

    def __init__(self, name, namespace):
        self.name = name
        self.namespace=namespace

    @property
    def logger(self):
        return getLogger(f'validation.{self.name}')


class _BaseValidator(Callable):

    def __init__(self
                 , treatment
                 , level
                 , name=''
                 ):
        self.treatment = treatment
        self.level=level
        self.name=name

    def __call__(self, value: Series, cvalue: Series, *args, **kwargs):

        assert isinstance(value, Series) and isinstance(cvalue, Series)

        def process():
            VAL_LOGGER.debug(f'{self.name} treat')
            ret = self.treatment(x=value, y=cvalue)
            return ret

        res = process()
        if res is not None:
            res['val'] = self.name
            res['level'] = self.level
            res.set_index(['val'], append=True, inplace=True)
        return res




class _BaseManyValidators(Callable):

    def __init__(self, *args, name: str, cvalue, prep_foo: Callable = None):
        """
        Many validators, that validate the same cvalue
        :param name: name of validator
        :param cvalue: target value
        :param prep_foo: function(data: DataFrame) to treat incoming values
        :param args: tuple(log level, function(value, cvalue) that validate target value)
        """
        self.cvalue = cvalue
        self.name = name
        for c in args:
            if not (isinstance(c, tuple) and len(c) == 2):
                raise Exception('args must be tuples of exact size: 2')
        self.prep_foo = prep_foo
        self.validators = [
            _BaseValidator(treat, level, name=name) for level, treat in args
        ]

    def __call__(self, value, *args, **kwargs):
        if self.prep_foo:
            VAL_LOGGER.debug(f'Prepare data for {self.name} validator')
            value = self.prep_foo(value)
            if not isinstance(value, Series):
                raise TypeError(f'{self.prep_foo} must return Series, but returned {value}')
        res = []
        for x in self.validators:
            _res = x(value, self.cvalue)
            if _res is not None:
                res.append(_res)
                break
        return concat(res) if res else None

class _PrepValidator(Callable):
    """
    Hold all the parameters to make Validators class and make it an call using cvalue=prep_foo(data)
    """
    def __init__(self, name: str, prep_foo: Callable, *args):
        self.prep_foo = prep_foo
        self.name = name
        self.args = args

    def __call__(self, data: DataFrame):
        return _BaseManyValidators(name=self.name
                                   , cvalue=self.prep_foo(data)
                                   , prep_foo=self.prep_foo
                                   , *self.args)
