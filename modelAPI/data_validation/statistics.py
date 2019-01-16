from pandas import DataFrame, Series
from datetime import date


def nans(data: DataFrame):
    return (data.isna().sum() / data.shape[0]).round(4) + 0.0001


def dtypes(data: DataFrame):
    return data.dtypes


def mean(data: DataFrame):
    return data.select_dtypes('number').mean().round(4) + 0.0001


def uniques(data: DataFrame):
    return data.nunique() / data.shape[0] + 0.000001


def has_text(data: DataFrame):
    return data.applymap(lambda x: isinstance(x, str)).max()


def has_dates(data: DataFrame):
    return data.applymap(lambda x: isinstance(x, date)).max()


def pass_through(data: DataFrame):
    return data.stack()

def quantiles(data: DataFrame):

    def quant(_data: Series, n_quant=5):
        return {
            f'buck_{n}': _data.quantile((n+1) / (n_quant+1)) for n in range(n_quant)
        }
    return data.select_dtypes('number').apply(quant, result_type='expand').T.stack().round(4)

def data_len(data: DataFrame):
    return Series([data.shape[0]], ['data_len'])


def columns(data: DataFrame):
    return Series(data.columns)
