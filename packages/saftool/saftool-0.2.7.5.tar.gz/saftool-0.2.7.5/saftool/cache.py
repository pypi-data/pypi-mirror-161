# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     cache
   Description :   用于保存全局变量
   Author :        Asdil
   date：          2020/10/29
-------------------------------------------------
   Change Activity:
                   2022/08/03:
-------------------------------------------------
"""
__author__ = 'Asdil'
import sys


class Cache:
    """
    Cache类用于懒惰加载数据, 这是全局的
    """
    def get(self, attr):
        """get方法用于取数据(类似字典)
        Parameters
        ----------
        attr : str
            需要取出的字段名
        Returns
        ----------
        """
        if attr in self.__dict__.keys():
            return self.__getattribute__(attr)
        else:
            return None

    def set(self, key, value):
        """set方法用于存储数据
        Parameters
        ----------
        key : str
            关键字
        value : anything
            需要存储的数据,任意类型
        Returns
        ----------
        """
        self.__setattr__(key, value)

    def upset(self, key, value):
        """upset方法用于插入或者更新存储数据
        Parameters
        ----------
        key : str
            关键字
        value : anything
            需要存储的数据,任意类型
        Returns
        ----------
        """
        if key in self.__dict__.keys():
            self.__dict__[key] = value
        else:
            self.__setattr__(key, value)


# 加入系统识别
sys.modules[__name__] = Cache()
