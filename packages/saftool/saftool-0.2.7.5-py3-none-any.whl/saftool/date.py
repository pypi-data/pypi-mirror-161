# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     date
   Description :   用于处理日期
   Author :        Asdil
   date：          2020/10/9
-------------------------------------------------
   Change Activity:
                   2020/10/9:
-------------------------------------------------
"""
__author__ = 'Asdil'
import time
from datetime import datetime
from dateutil.parser import parse


def str_to_datetime(date):
    """str_to_datetime方法用于字符串转日期
    Parameters
    ----------
    date : str
        日期字符串：
        eg:
        2018-10-21
        20181021
        2018/10/21
        10-21 # 如果没有年份默认今年
        10/21
    Returns
    ----------
    datetime
    """
    return parse(date)


def datetime_to_str(date, milliseconds=False):
    """datetime_to_str方法用于日期转字符串

    Parameters
    ----------
    date : datetime
        日期
    milliseconds: bool
        是否保留毫秒
    Returns
    ----------
    """
    if milliseconds:
        return date.isoformat(sep=' ', timespec='milliseconds')
    else:
        return date.replace(microsecond=0).isoformat(' ')


def timestamp_to_datetime(timestamp):
    """timestamp_to_str方法用于时间戳转日期字符串
    time.time() 转 datetime
    Parameters
    ----------
    timestamp : float
        时间戳
    Returns
    ----------
    """
    return datetime.fromtimestamp(timestamp)


def datetime_to_timestamp(date):
    """datetime_to_timestamp方法用于日期转时间戳

    Parameters
    ----------
    date : datetime
        日期
    Returns
    ----------
    """
    return datetime.timestamp(date)


def timestamp_to_str(timestamp, milliseconds=False):
    """timestamp_to_str方法用于时间戳转日期字符串
    time.time()
    Parameters
    ----------
    timestamp : float
        时间戳
    milliseconds : bool
        保留毫秒
    Returns
    ----------
    """
    date = timestamp_to_datetime(timestamp)
    return datetime_to_str(date, milliseconds)


def now_str(format_type=2):
    """now_str方法用于返回当前时间,字符串类型

    Parameters
    ----------
    format_type : int
        显示类型
        0: 年月日时分秒
        1: 年-月-日 时:分:秒
        2: 年月日时分
        3: 年-月-日
    Returns
    ----------
    """
    if format_type == 0:
        return time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    elif format_type == 1:
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    elif format_type == 2:
        return time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
    else:
        return time.strftime('%Y-%m-%d', time.localtime(time.time()))


if __name__ == "__main__":
    import time
    from datetime import timedelta
    a = datetime.now() + timedelta(days=1)
    print(a)
