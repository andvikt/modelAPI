from . import statistics as stats
from . import treatments as tr
from .helpers import _PrepValidator
from logging import WARNING, ERROR


VAL_DATA_SCHEMA = [
    _PrepValidator('dtypes', stats.dtypes, (WARNING, tr.not_match))
    , _PrepValidator('has_text', stats.has_text, (ERROR, tr.ne))
    , _PrepValidator('has_dates', stats.has_dates, (ERROR, tr.ne))
    , _PrepValidator('nans', stats.nans, (ERROR, tr.high_diff), (WARNING, tr.low_diff))
    , _PrepValidator('mean', stats.mean, (ERROR, tr.high_diff), (WARNING, tr.low_diff))
    , _PrepValidator('uniques', stats.uniques, (ERROR, tr.high_diff), (WARNING, tr.low_diff))
    , _PrepValidator('quant', stats.quantiles, (WARNING, tr.low_diff))
]

VAL_EXACT_DATA = [
    _PrepValidator('data_len', stats.data_len, (ERROR, tr.ne))
    , _PrepValidator('exact_match', stats.pass_throgh, (ERROR, tr.ne))
]

