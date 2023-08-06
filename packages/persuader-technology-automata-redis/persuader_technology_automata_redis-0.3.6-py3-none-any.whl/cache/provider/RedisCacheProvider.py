import logging
from typing import TypeVar

import redis
from core.constants.not_available import NOT_AVAILABLE
from core.number.BigFloat import BigFloat
from core.options.exception.MissingOptionError import MissingOptionError
from coreutility.json.json_utility import as_json, as_pretty_json

T = TypeVar("T")

REDIS_SERVER_ADDRESS = 'REDIS_SERVER_ADDRESS'
REDIS_SERVER_PORT = 'REDIS_SERVER_PORT'


class RedisCacheProvider:

    def __init__(self, options, auto_connect=True):
        self.log = logging.getLogger('RedisCacheProvider')
        self.options = options
        self.auto_connect = auto_connect
        self.__check_options()
        if self.auto_connect:
            self.server_address = options[REDIS_SERVER_ADDRESS]
            self.server_port = options[REDIS_SERVER_PORT]
            self.log.info(f'Connecting to REDIS server {self.server_address}:{self.server_port}')
            self.redis_client = redis.Redis(host=self.server_address, port=self.server_port, decode_responses=True)

    def __check_options(self):
        if self.options is None:
            self.log.warning(f'missing option please provide options {REDIS_SERVER_ADDRESS} and {REDIS_SERVER_PORT}')
            raise MissingOptionError(f'missing option please provide options {REDIS_SERVER_ADDRESS} and {REDIS_SERVER_PORT}')
        if self.auto_connect is True:
            if REDIS_SERVER_ADDRESS not in self.options:
                self.log.warning(f'missing option please provide option {REDIS_SERVER_ADDRESS}')
                raise MissingOptionError(f'missing option please provide option {REDIS_SERVER_ADDRESS}')
            if REDIS_SERVER_PORT not in self.options:
                self.log.warning(f'missing option please provide option {REDIS_SERVER_PORT}')
                raise MissingOptionError(f'missing option please provide option {REDIS_SERVER_PORT}')

    def can_connect(self):
        try:
            return self.redis_client.ping()
        except redis.exceptions.ConnectionError:
            return False

    def get_keys(self, pattern='*'):
        return self.redis_client.keys(pattern)

    def store(self, key, value):
        self.log.debug(f'storing for key:{key}')
        if type(value) is BigFloat:
            self.log.debug(f'BigFloat storing key:{key} [{value}]')
            self.redis_client.set(key, str(value))
        elif type(value) is dict:
            self.log.debug(f'collection storing key:{key} [{value}]')
            serialized_json = as_pretty_json(value, indent=None)
            self.redis_client.set(key, serialized_json)
        else:
            self.log.debug(f'default storing key:{key} [{value}]')
            self.redis_client.set(key, value)

    def fetch(self, key, as_type: T = str):
        value = self.redis_client.get(key)
        if value is not None and value == NOT_AVAILABLE:
            return NOT_AVAILABLE
        if as_type is int:
            return None if value is None else int(value)
        elif as_type is float:
            return None if value is None else float(value)
        elif as_type is BigFloat:
            return None if value is None else BigFloat(value)
        elif as_type is dict:
            result = as_json(value)
            self.log.debug(f'dict fetching key:{key} [{result}]')
            return None if len(result) == 0 else result
        else:
            return value

    def delete(self, key):
        return self.redis_client.delete(key)
