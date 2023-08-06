# -*- coding: utf-8 -*-
# @Time    : 2022/6/17 23:57
# @Author  : CC
# @Desc    : decr_reids_cache.py
import functools
import json

import redis


class RedisCache(object):

    def __init__(self, address, password=None, port=6379, db=0):
        self.address = address
        self.password = password
        self.port = port
        self.db = db
        if self.password:
            self._redis_conn = redis.Redis(host=self.address,
                                           port=self.port,
                                           db=self.db,
                                           password=self.password)
        else:
            self._redis_conn = redis.Redis(host=self.address,
                                           port=self.port,
                                           db=self.db)

    def get_cache(self, key):
        """
        GET method
        :param key: The key to GET
        """
        rs = self._redis_conn.get(key)
        if rs:
            return rs.decode()
        return None

    def set_cache(self, key, value):
        """
        SET method
        :param key: The key to SET
        :param value: The value of the key to SET
        """
        self._redis_conn.set(key, value)

    def set_cache_and_expire(self, key, value, expiration):
        """
        SETEX command
        :param key: The key to SET
        :param value: The value of the key to SET
        :param expiration: TTL in seconds
        """
        self._redis_conn.set(key, value)
        self._redis_conn.expire(key, expiration)

    def cache(*args, **kwargs):
        """缓存装饰器"""
        ttl = args[1] if len(args) >= 2 else (kwargs.get('ttl') if kwargs.get('ttl') else 6)
        self = args[0]

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                serialized_args = [str(arg) for arg in args]
                serialized_args.append(str(kwargs))
                key = ''.join(serialized_args)
                key = ':'.join([func.__name__, key])
                print(key)
                rs_redis = self.get_cache(key)
                if rs_redis:
                    if isinstance(rs_redis, str) and '###dict' in rs_redis:
                        rs_redis = json.loads(rs_redis.strip('###dict'))
                    return rs_redis
                else:
                    result = func(*args, **kwargs)
                    if result:
                        if isinstance(result, dict) or isinstance(result, list):
                            result_str = json.dumps(result)
                            self.set_cache_and_expire(key, result_str + "###dict", ttl)
                        else:
                            self.set_cache_and_expire(key, result, ttl)
                    return result

            return wrapper

        return decorator


if __name__ == '__main__':
    redis_cache = RedisCache('127.0.0.1')


    @redis_cache.cache(ttl=30)
    def sum_t(a, b):
        print(f'{a}+{b}={a + b}')
        return a + b


    r1 = sum_t(1, 2)
    print(r1)

    r2 = sum_t(4, 5)
    print(r2)
