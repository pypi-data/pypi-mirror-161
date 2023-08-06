# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     math
   Description :
   Author :        Asdil
   date：          2021/6/9
-------------------------------------------------
   Change Activity:
                   2021/6/9:
-------------------------------------------------
"""
__author__ = 'Asdil'
import numpy as np
from copy import deepcopy


def random_select(a, num, replace=False):
    """random_select方法用于

    Parameters
    ----------
    a : int or list or np.array
        随机选择数上限或者是列表
    num : int
        个数
    replace : bool
        是否有放回
    Returns
    ----------
    """
    if type(a) in {int, float, np.int8, np.int16, np.int32, np.int64,
                   np.float16, np.float32, np.float64}:
        high = int(a)
        rng = np.random.default_rng()
        ret = rng.choice(high, size=num, replace=replace)
        return ret

    high = len(a)
    rng = np.random.default_rng()
    indexs = rng.choice(high, size=num, replace=replace)
    ret = []
    for i in indexs:
        ret.append(deepcopy(a[i]))
    return ret


def max_min_index(indexes, values, typ='min'):
    """max_min_index方法用于查找最大最小索引的位置

    Parameters
    ----------
    indexes : list
        索引列表
    values : list
        值列表
    typ : str
        min 或者 max

    Returns
    ----------
    """
    if typ == 'min':
        i = np.argmin(values)
        return indexes[i]
    else:
        i = np.argmax(values)
        return indexes[i]
