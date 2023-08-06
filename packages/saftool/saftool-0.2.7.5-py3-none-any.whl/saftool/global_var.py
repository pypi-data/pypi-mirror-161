# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     global_var
   Description :   用于保存全局变量
   Author :        Asdil
   date：          2020/11/5
-------------------------------------------------
   Change Activity:
                   2022/08/03:
-------------------------------------------------
"""
__author__ = 'Asdil'


def __init():
    """__init方法用于初始化"""
    global __global_dict
    __global_dict = {}


def get(key):
    """get方法用于取出参数

    Parameters
    ----------
    key : str
        变量名称
    Returns
    ----------
    """
    if key not in __global_dict:
        raise KeyError('There is no variable named %s' % key)
    return __global_dict[key]


def set(key, value):
    """set方法用于保存变量

    Parameters
    ----------
    key : str or dict
        变量名或者字典
    value : anytype
        变量值
    Returns
    ----------
    """
    if type(key) is dict:
        for k in key:
            __global_dict[k] = key[k]
    else:
        __global_dict[key] = value


def keys():
    """keys方法用于获取所有变量名"""
    return list(__global_dict.keys())


__init()
