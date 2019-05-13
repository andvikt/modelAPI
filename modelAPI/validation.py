from typing import Iterable, Generic, TypeVar, Callable
import pandas as pd
from functools import wraps
from andormixin import AndOrMixin

X = TypeVar("X")
Y = TypeVar("Y")

class ValidationError(Exception): pass


class NotAllColumns(ValidationError):
    def __init__(self, columns, need_columns):
        self.columns = columns
        self.need_columns = need_columns
    def __repr__(self):
        return f'Missing columns: {set(self.need_columns) - set(self.columns)}'


class DtypeError(ValidationError):pass


class BaseValidator(AndOrMixin):

    def validate(self, data):
        return True


class ColumnValidation(BaseValidator):

    required_columns: tuple = None

    def validate(self, data):
        if set(self.required_columns).issubset(set(data.columns)):
            return True
        else:
            raise NotAllColumns(data.columns, self.required_columns)

    @classmethod
    def from_data(cls, data: pd.DataFrame):
        obj = cls()
        obj.required_columns = tuple(data.columns)


class DtypeValidation(ColumnValidation):

    dtypes: dict = None

    @classmethoddevp
    def from_data(cls, data:pd.DataFrame):
        obj = cls()
        obj.required_columns = tuple(data.columns)
        obj.dtypes = tuple(data.dtypes)

    def validate(self, data: pd.DataFrame):
        super().validate(data)
        for name, dtype in data.dtypes.to_dict().items():
            assert dtype is dtype[name]
