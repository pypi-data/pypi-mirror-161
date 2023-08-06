import redis
from core.number.BigFloat import BigFloat

from cache.provider.RedisCacheProviderWithHash import RedisCacheProviderWithHash
from cache.utility.BigFloat_utility import crack_to_serialize, join_to_deserialize


class RedisCacheProviderWithTimeSeries(RedisCacheProviderWithHash):

    def __init__(self, options, auto_connect=True):
        super().__init__(options, auto_connect)
        if self.auto_connect:
            self.redis_timeseries = self.redis_client.ts()

    @staticmethod
    def fraction_key(key):
        return f'{key}:d'

    @staticmethod
    def fraction_leading_zeros_key(key):
        return f'{key}:d:lz'

    def __create_timeseries(self, key, field_name, limit_retention):
        if not self.does_timeseries_exist(key):
            self.redis_timeseries.create(key, labels={'time': field_name}, retention_msecs=limit_retention)

    def create_timeseries(self, key, field_name, double_precision=False, limit_retention=0):
        self.__create_timeseries(key, field_name, limit_retention)
        if double_precision:
            self.__create_timeseries(self.fraction_key(key), field_name, limit_retention)
            self.__create_timeseries(self.fraction_leading_zeros_key(key), field_name, limit_retention)

    def add_to_timeseries(self, key, time, value):
        if type(value) is BigFloat:
            (number, decimal, leading_decimal_zeros) = crack_to_serialize(value)
            self.redis_timeseries.add(key, time, number)
            self.redis_timeseries.add(self.fraction_key(key), time, decimal)
            self.redis_timeseries.add(self.fraction_leading_zeros_key(key), time, leading_decimal_zeros)
        else:
            self.redis_timeseries.add(key, time, value)

    def get_timeseries_data(self, key, time_from, time_to, double_precision=False, reverse_direction=False):
        if double_precision:
            if reverse_direction is False:
                number_values = self.redis_timeseries.range(key, time_from, time_to)
                fraction_values = self.redis_timeseries.range(self.fraction_key(key), time_from, time_to)
                fraction_leading_zero_values = self.redis_timeseries.range(self.fraction_leading_zeros_key(key), time_from, time_to)
                return [(n1, join_to_deserialize(int(v1), int(v2), int(v3))) for (n1, v1), (f2, v2), (l3, v3) in zip(number_values, fraction_values, fraction_leading_zero_values) if n1 == f2 and n1 == l3]
            else:
                number_values = self.redis_timeseries.revrange(key, time_from, time_to)
                fraction_values = self.redis_timeseries.revrange(self.fraction_key(key), time_from, time_to)
                fraction_leading_zero_values = self.redis_timeseries.revrange(self.fraction_leading_zeros_key(key), time_from, time_to)
                return [(n1, join_to_deserialize(int(v1), int(v2), int(v3))) for (n1, v1), (f2, v2), (l3, v3) in zip(number_values, fraction_values, fraction_leading_zero_values) if n1 == f2 and n1 == l3]
        else:
            if reverse_direction is False:
                return self.redis_timeseries.range(key, time_from, time_to)
            else:
                return self.redis_timeseries.revrange(key, time_from, time_to)

    def does_timeseries_exist(self, timeseries_key):
        try:
            self.redis_timeseries.info(timeseries_key)
            return True
        except redis.exceptions.ResponseError:
            return False

    def delete_timeseries(self, key, double_precision=False):
        self.delete(key)
        if double_precision:
            self.delete(self.fraction_key(key))
            self.delete(self.fraction_leading_zeros_key(key))

    def get_timeseries_retention_time(self, timeseries_key):
        info = self.redis_timeseries.info(timeseries_key)
        return info.retention_msecs
