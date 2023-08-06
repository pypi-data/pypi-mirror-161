# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     log
   Description :
   Author :        Asdil
   date：          2020/10/9
-------------------------------------------------
   Change Activity:
                   2020/10/9:
-------------------------------------------------
"""
__author__ = 'Asdil'
import logging
from logging.handlers import RotatingFileHandler


def simple_init(log_path=None, level='INFO', rotation=1, format_type=0):
    """add方法用于新建一个log

    Parameters
    ----------
    level: str
        日志级别
    log_path: str
        保存路径
    rotation : int
        每个日志大小MB计算
    format_type : int
        输出格式种类
    Returns
    ----------
    """
    # 日志详细程度
    formats = {0: '%(asctime)s | %(levelname)s | pid:%(process)d |%(filename)s:%(funcName)s:%(lineno)s - %(message)s',
               1: '%(asctime)s | %(levelname)s |%(filename)s:%(funcName)s:%(lineno)s - %(message)s',
               2: '%(asctime)s |%(filename)s:%(funcName)s:%(lineno)s - %(message)s',
               }
    logger = logging.getLogger()
    level_dict = {'DEBUG': logging.DEBUG, 'INFO': logging.INFO, 'WARNING': logging.WARNING, 'ERROR': logging.ERROR}
    logger.setLevel(level_dict[level])

    handler = None

    if log_path is not None:
        # create a file handler
        handler = RotatingFileHandler(filename=log_path, maxBytes=rotation * 1024 * 1024, encoding='utf-8')
        handler.setLevel(level)
        # create a logging format
        formatter = logging.Formatter(formats[format_type])
        handler.setFormatter(formatter)

    # add the handlers to the logger
    if handler:
        logger.addHandler(handler)
    return logger
