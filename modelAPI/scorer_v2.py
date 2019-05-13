"""
Base implementation of Abstract model class
"""

from pandas import DataFrame, Series

from modelAPI.validation import BaseValidator
from .utils.logger import _LoggerMixin
from .utils.saver import _SelfSaving
from typing import Callable


class BaseScorer(object):

    data_validator: BaseValidator = None


class BaseScorer (_LoggerMixin, _SelfSaving):
    """
    Abstract scorer class
    Subclasses must override _score(data:DataFrame)
    """

    check_output_shape = True

    def __init__(self
                 , columns_required: list
                 , params: dict = dict()
                 , name: str = 'scorer'
                 ):
        """

        :param name:
        :param columns_required:
        :param params: will be passed to _score function as params
        """
        assert isinstance(columns_required, list)
        self.columns_required = columns_required
        assert isinstance(params, dict)
        self.params = params
        _LoggerMixin.__init__(self, name=name, namespace='scorer')
        _SelfSaving.__init__(self, save_list={'_score'})

    @staticmethod
    def _score(data: DataFrame, **kwargs) -> DataFrame:
        raise NotImplementedError

    def score(self, data: DataFrame, **kwargs) -> DataFrame:
        """
        Score data with _score, check that output is the same size as input
        :param data:
        :param kwargs: additional data, required for scoring, will be appended to self.params
        :return:
        """
        self.logger.info(f'Begin scoring {self.name}')
        self._check_columns(data)
        _input = data[self.columns_required].copy()
        input_size = _input.shape[0]
        kwargs.update(self.params)
        ret = self._score(_input, **kwargs)
        if isinstance(ret, Series):
            ret = ret.to_frame('score')
        if ret.shape[0] != input_size and self.check_output_shape:
            raise Exception(f"Score returns {ret.shape[0]} records, but provided {input_size}")
        return ret

    def _check_columns(self, data:DataFrame):
        columns = set(data.columns)
        if not set(self.columns_required).issubset(columns):
            raise Exception(f'Not all required columns are provided')

    @classmethod
    def make_scorer(cls
                    , score_foo: Callable
                    , columns_required: list
                    , name: str = 'scorer'
                    , check_output_shape=True
                    , **params):
        """
        Make scorer with score_foo as main scoring function, passes kwargs to object with setattr
            all kwargs will be passed to score_foo asis and also will be set on a object as attribute, so it can be
            then pickled with the rest of object contents
        :param score_foo: Callable, base scoring functionality, must return Series or DataFrame with the same
        :param name: name of a scorer, needed for better logging
        :param columns_required: list of column names, required for scoring in order of their presence
        :param params: dict of additional data, required for scoring (instances of other models for example)
        :return: Scorer
        """
        ret = cls(name=name, columns_required=columns_required, params=params)
        ret.check_output_shape=check_output_shape
        ret._score = score_foo
        return ret
