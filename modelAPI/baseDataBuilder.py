from .utils.logger import _LoggerMixin
from .utils.saver import _SelfSaving
from pandas import DataFrame
from typing import Callable, Coroutine
import voluptuous as vol


class BaseDataBuilder(_LoggerMixin, _SelfSaving):
    """
    Base data builder
    """

    def __init__(self
                 , required_params: vol.Schema = None
                 , name='builder'
                 , fixed_params: dict = None
                 ):
        self.required_params = required_params
        self.fixed_params=fixed_params
        _LoggerMixin.__init__(self, name=name, namespace='data_builder')
        _SelfSaving.__init__(self, save_list={'_build', '_build_async'})

    @staticmethod
    def _build(**kwargs) -> DataFrame:
        raise NotImplementedError

    @staticmethod
    async def _build_async(**kwargs) -> DataFrame:
        raise NotImplementedError

    def build(self, **kwargs) -> DataFrame:
        if self.required_params:
            kwargs = self.required_params(kwargs)
        kwargs.update(self.fixed_params)
        return self._build(**kwargs)

    async def async_build(self, **kwargs):
        if self.required_params:
            kwargs = self.required_params(kwargs)
        kwargs.update(self.fixed_params)
        return await self._build_async(**kwargs)

    @classmethod
    def make_builder(cls
                     , build_foo: Callable = None
                     , build_async_foo: Coroutine = None
                     , required_params: vol.Schema = None
                     , name: str = 'builder'
                     , fixed_params: dict = None
                     ):
        """
        Make new DataBuilder using foo or async_foo as main data building process
        :param build_foo: builder function, must return DataFrame
        :param build_async_foo: async builder function, must return DataFrame
        :param required_params: volouptous schema to check all the parameters are passed and right
        :param name: name of builder
        :param fixed_params: some parametrs, that will be passed to builder on each call to build
        :return: cls
        """
        assert build_foo is not None or build_async_foo is not None
        ret = cls(required_params=required_params, name=name, fixed_params=fixed_params)
        if build_foo is not None:
            ret.build = build_foo
        if build_async_foo is not None:
            ret.async_build = build_async_foo
        return ret
