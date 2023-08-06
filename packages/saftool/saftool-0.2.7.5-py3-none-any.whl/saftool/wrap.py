# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     wrap
   Description :
   Author :       asdil
   date：          2022/1/17
-------------------------------------------------
   Change Activity:
                   2022/1/17:
-------------------------------------------------
"""
__author__ = 'Asdil'

import time
import functools
from datetime import datetime
from concurrent import futures
from functools import lru_cache
# 重复执行缓存@lru_cache

executor = futures.ThreadPoolExecutor(1)


def type_assert(*ty_args, **ty_kwargs):
    """type_assert方法用于强制确认输入格式

    @type_assert(int, b=str)
    f(a, b)

    Parameters
    ----------
    Returns
    ----------
    """
    from inspect import signature
    from functools import wraps

    def decorate(func):
        # If in optimized mode, disable type checking
        if not __debug__:
            return func

        # Map function argument names to supplied types
        sig = signature(func)
        bound_types = sig.bind_partial(*ty_args, **ty_kwargs).arguments

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound_values = sig.bind(*args, **kwargs)
            # Enforce type assertions across supplied arguments
            for name, value in bound_values.arguments.items():
                if name in bound_types:
                    if not isinstance(value, bound_types[name]):
                        raise TypeError(
                            'Argument {} must be {}'.format(
                                name, bound_types[name]))
            return func(*args, **kwargs)
        return wrapper
    return decorate


def runtime(func):
    """runtime方法用于, 运行时间的装饰器

    Parameters
    ----------
    func : function
        函数对象

    Returns
    ----------
    """
    def wrapper(*args, **kwargs):
        start_now = datetime.now()
        start_time = time.time()
        ret = func(*args, **kwargs)
        end_time = time.time()
        end_now = datetime.now()
        print(f'time时间:{end_time-start_time}\ndatetime起始时间:{start_now} 结束时间:{end_now}, 一共用时{end_now-start_now}')
        return ret
    return wrapper


def timeout(seconds):
    """timeout方法用于设置超时

    Parameters
    ----------
    seconds : int
        秒数

    Returns
    ----------
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            future = executor.submit(func, *args, **kw)
            return future.result(timeout=seconds)
        return wrapper
    return decorator


class AllowCount:
    """
    allow_count类用于约束函数执行次数
    """
    def __init__(self, count):
        """__init__(self):方法用于初始化

        Parameters
        ----------
        count : int
            最大执行次数

        Returns
        ----------
        """
        self.count = count
        self.i = 0
    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            if self.i >= self.count:
                return
            self.i += 1
            return func(*args, **kw)
        return wrapper


def helping():
    """helping方法用于输出可用修饰器"""
    print(' @type_assert(int, b=str) 强制定义输入种类')
    print(' @runtime 运行时长')
    print(' @timeout(seconds) 设置超时')
    print(' @lru_cache() 多次执行缓存')
    print(' @AllowCount(2) 强制定义函数可行性次数')
