from .helpers import _PrepValidator, _LoggerMixin
from ..utils.saver import _SelfSaving
from pandas import DataFrame, concat
from typing import Sequence
from modelAPI.data_validation.helpers import VAL_LOGGER, LEVELS
from logging import Logger
import os


class DataValidator(_LoggerMixin, _SelfSaving):
    """
    Валидатор, запоминает статистику о данных, чтобы в будущем на новых данных проверить отклонение от базовых статистик
    Для расчета и проверки статистик используется val_schema, может быть определена пользователем, но лучше всего
    использовать готовые схемы из modelAPI.val_schemas

    Пример:

    from modelAPI import DataValidator, val_schemas
    validator = DataValidator(data, val_schemas.VAL_DATA_SCHEMA)
    validator(new_data)

    Если не нужно поднимать ошибки в явном виде, а лишь увидеть вывод ошибки в логе, можно выполнить:

    from modelAPI inport set_val_raise
    set_val_raise(False)

    """
    def __init__(self
                 , init_data: DataFrame = None
                 , val_schema: Sequence[_PrepValidator] = None
                 , name: str = 'validate'
                 ):
        """
        :param init_data: initial data for calculating base statics
        :param val_schema: validation schema
        """
        super().__init__(name=name, namespace='validator')
        _SelfSaving.__init__(self, save_list={'validators', 'name'})
        self.logger.info(f'prepare validation data')
        self.validators = [
            x(data=init_data) for x in val_schema
        ]

    def __call__(self, data: DataFrame, raise_on_error:bool=False) -> DataFrame:
        """
        Validate data
        :param data: data for validation
        :param raise_on_error: bool
        """
        ret = [x(data) for x in self.validators]
        ret = [x for x in ret if x is not None]
        ret = concat(ret) if ret else None
        if ret is not None:
            ret.sort_values(['level'], ascending=False)
            for (idx, control, passed, level) in ret.itertuples():
                self.logger.log(level, f"{idx}: C: {control}; P: {passed}")
            ret['level'] = ret['level'].map(LEVELS)
            if (ret['level'] == 'error').max() and raise_on_error:
                report_fname = f'{self.namespace}.{self.name}.xls'
                self.logger.error(f'Validation of {self.name} passed with errors, look at {os.getcwd()}\{report_fname}:\n{ret}')
                ret.to_excel(report_fname)
                raise Exception(f'Validation of {self.name} passed with errors')
        return ret
