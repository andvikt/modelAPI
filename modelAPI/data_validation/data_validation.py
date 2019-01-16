from .helpers import _PrepValidator, _LoggerMixin
from pandas import DataFrame, concat
from typing import Sequence
from modelAPI.data_validation.helpers import VAL_LOGGER, LEVELS
from logging import Logger


class DataValidator(_LoggerMixin):
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
                 , init_data: DataFrame
                 , val_schema: Sequence[_PrepValidator]
                 , name: str
                 ):
        """
        :param init_data: initial data for calculating base statics
        :param val_schema: validation schema
        """
        super().__init__(name=name, namespace='validator')
        self.logger.info(f'prepare validation data')
        self.validators = [
            x(data=init_data) for x in val_schema
        ]

    def __call__(self, data: DataFrame) -> DataFrame:
        """
        Validate data
        :param data: data for validation
        """
        ret = [x(data) for x in self.validators]
        ret = [x for x in ret if x is not None]
        ret = concat(ret) if ret else None
        if ret is not None:
            ret.sort_values(['level'], ascending=False)
            ret['level'] = ret['level'].map(LEVELS)
        return ret
