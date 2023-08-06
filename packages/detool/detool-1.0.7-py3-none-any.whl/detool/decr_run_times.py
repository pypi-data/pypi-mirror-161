# -*- coding: utf-8 -*-
# @Time    : 2022/6/9 22:49
# @Author  : CC
# @Desc    : decr_run_times.py
import functools


def repeat(_func=None, *, num_times=2):
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper_repeat(*args, **kwargs):
            for _ in range(num_times):
                value = func(*args, **kwargs)
            return value

        return wrapper_repeat

    if _func is None:
        return decorator_repeat
    else:
        return decorator_repeat(_func)


if __name__ == '__main__':
    @repeat(num_times=3)
    def t(a, b):
        print(a+b)
        return a + b


    s = t(3, 6)
    print(s)
