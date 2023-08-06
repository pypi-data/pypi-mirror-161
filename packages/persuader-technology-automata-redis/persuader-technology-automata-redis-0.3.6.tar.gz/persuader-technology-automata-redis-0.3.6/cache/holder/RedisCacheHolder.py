import logging
from typing import TypeVar, Type

from cache.provider.RedisCacheProvider import RedisCacheProvider
from cache.provider.RedisCacheProviderWithHash import RedisCacheProviderWithHash
from cache.provider.RedisCacheProviderWithTimeSeries import RedisCacheProviderWithTimeSeries

T = TypeVar('T', RedisCacheProvider, RedisCacheProviderWithHash, RedisCacheProviderWithTimeSeries)


# todo: nice, would be just RedisCacheHolder(Generic[T]) (IDE having trouble)
class RedisCacheHolder:
    __instance: T = None

    def __new__(cls, options=None, held_type: Type[T] = RedisCacheProvider) -> T:
        if cls.__instance is None:
            log = logging.getLogger('RedisCacheHolder')
            log.info(f'Holder obtaining REDIS cache provider with options:{options}')
            auto_connect = cls.set_auto_connect(options)
            cls.__instance = held_type(options, auto_connect)
        return cls.__instance

    @staticmethod
    def set_auto_connect(options):
        if options is None:
            return False
        if 'AUTO_CONNECT' not in options:
            return True
        return options['AUTO_CONNECT']

    @staticmethod
    def re_initialize():
        RedisCacheHolder.__instance = None
