# -*- coding: utf-8 -*-
# @Time    : 2022/6/7 22:35
# @Author  : CC
# @Desc    : 计算函数运行时长
import functools
import time
from loguru import logger


def timer_cost(func):
    """
    计算函数执行时间(秒)装饰器
    """

    @functools.wraps(func)
    def time_cal(*args, **argus):
        time_begin = time.time()
        rs = func(*args, **argus)
        time_end = time.time()
        cost_time = round((time_end * 1000 - time_begin * 1000) / 1000, 2)
        logger.info(f"{func.__name__} cost time:{cost_time}S")
        return rs

    return time_cal


if __name__ == '__main__':
    @timer_cost
    def t_time():
        time.sleep(0.01)
        print(123)


    class A(object):

        @timer_cost
        def t(self):
            print(345)


    t_time()
    A().t()
