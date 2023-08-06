# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     tool
   Description :
   Author :        Asdil
   date：          2020/9/30
-------------------------------------------------
   Change Activity:
                   2020/9/30:
-------------------------------------------------
"""
__author__ = 'Asdil'


import os
import ast
import sys
import math
import shutil
import subprocess
from tqdm import tqdm
import importlib.machinery
from collections import Counter


def bar(data):
    """bar方法用于进度条

    Parameters
    ----------
    data : int or list or dict or iterator

    Returns
    ----------
    """
    if isinstance(data, int):
        return tqdm(range(data))
    return tqdm(data)


def safe_eval(string):
    """方法用于字符串转为对象

    Parameters
    ----------
    string : str
        需要转换的字符串

    Returns
    ----------
    """
    try:
        ret = ast.literal_eval(string)
    except:
        try:
            ret = eval(ret)
        except:
            raise ValueError(f"""错误! 无法转化语句: {string} """)
    return ret


def load_py_func(py_name, func_name='pipeline', py_dir='./'):
    """load_py方法用于动态加载py文件
    这加载的是指定的python文件函数

    Parameters
    ----------
    py_name : str
        py文件名称
    func_name : str
        函数名称 默认为 pipeline
    py_dir : str
        py文件路径
    Returns
    ----------
    """
    if '.py' != py_name[-3:]:
        py_name = py_name + '.py'
    py_dir = path_join(py_dir, py_name)
    # import py文件
    try:
        # import py文件
        module = importlib.machinery.SourceFileLoader(py_name, py_dir).load_module()
        func = getattr(module, func_name)
    except:
        raise ValueError(f'{py_name} 不存在, 或者没有{func_name} 函数')
    return func


def load_py(py_name, py_dir='./'):
    """load_py方法用于动态加载py文件

    Parameters
    ----------
    py_name : str
        py文件名称
    py_dir : str
        py文件所在的文件夹

    Returns
    ----------
    """
    if '.py' != py_name[-3:]:
        py_name = py_name + '.py'
    py_dir = path_join(py_dir, py_name)
    try:
        # import py文件
        module = importlib.machinery.SourceFileLoader(py_name, py_dir).load_module()
    except:
        raise ValueError(f'{py_name} 不存在')
    return module


def is_number(data):
    """is_number方法用于判断是否为数字

    Parameters
    ----------
    data :
        任意数据
    Returns
    ----------
    """
    try:
        float(data)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(data)
        return True
    except (TypeError, ValueError):
        pass
    return False


def bins_by_step(start, end, step):
    """bins_by_step方法用于等距分箱

    Parameters
    ----------
    start : float
        最小值
    end : float
        最大值
    step : float
        步长

    Returns
    ----------
    """
    if start >= end:
        raise ValueError(u'start is greater than or equal to end')
    ret = [start]
    while True:
        if ret[-1] + step >= end:
            if ret[-1] == end:
                break
            ret.append(end)
            break
        ret.append(ret[-1] + step)
    return ret


def counter(data, n=None):
    """counter方法用于统计元素数量

    Parameters
    ----------
    data : list
        列表数据
    n : int
        前n个元素
    Returns
    ----------
    """
    ret = Counter(data)
    if not n:
        ret = ret.most_common(len(ret))
    else:
        ret = ret.most_common(n)
    return ret


def is_nan(data, is_str=False):
    """is_nan方法用于判断是不是空值

    Parameters
    ----------
    data : anytype
        任何数据类型
    is_str : bool
        是否需要考虑字符型
    Returns
    ----------
    """
    if data is None:
        return True
    if is_str:
        if type(data) is str:
            if data.lower() in {'none', 'nan'}:
                return True
    try:
        return math.isnan(data)
    except:
        return False


def filter_nan(data):
    """filter_na方法用于过滤None值

    Parameters
    ----------
    data : list
        数据列表

    Returns
    ----------
    """
    return list(filter(lambda x: not is_nan(x), data))


def is_type(data, typ):
    """is_type方法用于判断数据类型

    Parameters
    ----------
    data : object
        任何数据
    typ : object
        需要确认的数据类型
    Returns
    ----------
    """
    if type(data) is typ:
        return True
    return False


def sort_list(data, ind, ascending=True):
    """sort_list方法用于排序列表，多维列表

    Parameters
    ----------
    data : list
        列表
    ind : int
        第几列
    ascending : pool
        升序或降序
    Returns
    ----------
    """
    if ascending:
        data = sorted(data, key=lambda x: x[ind])
    else:
        data = sorted(data, key=lambda x: -x[ind])
    return data


def path_join(path1, path2):
    """path_join方法用于合并两个或多个目录

    Parameters
    ----------
    path1 : str
        主路径
    path2 : str or list
        子路径
    Returns
    ----------
    """
    assert isinstance(path1, str)
    if isinstance(path2, list):
        path2 = os.sep.join(path2)
    if path1[-1] != os.sep:
        path1 += os.sep
    if path2[0] == os.sep:
        path2 = path2[1:]
    return path1 + path2


def get_files(path, extension=None, exclude=None, include=None):
    """get_files方法用于获取目录文件

        Parameters
        ----------
        path : str
            路径
        extension : str
            后缀
        exclude : str
            包含不包含某个词
        include : str
            包含某个词

        Returns
        ----------
        """
    ret = os.listdir(path)
    if extension:
        length = -len(extension)
        ret = list(filter(lambda x: x[length:] == extension, ret))
        if not ret:
            return []
    if exclude:
        ret = list(filter(lambda x: exclude not in x, ret))
        if not ret:
            return []
    if include:
        ret = list(filter(lambda x: include in x, ret))
        if not ret:
            return []
    ret = [path_join(path, each) for each in ret]
    return ret


def get_name(path, extension=None, include=None):
    """get_name方法用于

    Parameters
    ----------
    path : str
        路径
    extension : str or None
        后缀
    include : str or None
        包含某个字符
    Returns
    ----------
    """
    if extension is not None:
        l = -len(extension)
        ret = [each for each in os.listdir(path) if each[l:] == extension]
    elif include is not None:
        ret = [each for each in os.listdir(path) if include in each]
    else:
        ret = [each for each in os.listdir(path)]
    return ret


def subprocess_check_call(cmd):
    """subprocess_check_call方法用于执行命令行命令

    Parameters
    ----------
    cmd : str
        命令行命令

    Returns
    ----------
    """
    subprocess.check_call(cmd, shell=True)


def subprocess_call(cmd):
    """subprocess_call方法用于执行命令行命令，不检查是否执行成功

    Parameters
    ----------
    cmd : str
        命令行命令

    Returns
    ----------
    """
    subprocess.call(cmd, shell=True)


def subprocess_popen(cmd):
    """subprocess_popen方法用于执行命令获取返回值

    Parameters
    ----------
    cmd : str
        命令行命令

    Returns
    ----------
    """
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    out, err = p.communicate()
    return [each for each in out.decode('utf8').splitlines()]


def split_path(path):
    """
    拆分目录
    eg: '/tmp/tmp/a.txt'
        '/tmp/tmp', 'a', '.txt', 'a.txt'
    :param path: 路径
    :return:
    """
    assert isinstance(path, str)
    if path[-1] == os.sep:
        path = path[:-1]
    file_path, file_full_name = os.path.split(path)
    file_name, extension = os.path.splitext(file_full_name)
    return file_path, file_name, extension, file_full_name


def inter_set(l1, l2):
    """inter_set方法用于列表交集

    Parameters
    ----------
    l1 : list or set or dict
        列表或者集合
    l2 : list or set or dict
        列表或者集合

    Returns
    ----------
    """
    assert type(l1) in {list, set, dict}
    assert type(l2) in {list, set, dict}
    if type(l1) is dict:
        l1 = list(l1.keys())
        l2 = list(l2.keys())
    return list(set(l1).intersection(set(l2)))


def inter_set_num(l1, l2):
    """inter_set_num方法用于找交集数量

    Parameters
    ----------
    l1 : list or set or dict
        列表1
    l2 : list or set or dict
        列表2

    Returns
    ----------
    """
    assert type(l1) in {list, set, dict}
    assert type(l2) in {list, set, dict}
    if type(l1) is dict:
        l1 = list(l1.keys())
        l2 = list(l2.keys())
    return len(set(l1).intersection(set(l2)))


def diff_set(l1, l2):
    """diff_set方法用于找差集

    Parameters
    ----------
    l1 : list or set or dict
        列表1
    l2 : list or set or dict
        列表2

    Returns
    ----------
    """
    assert type(l1) in {list, set, dict}
    assert type(l2) in {list, set, dict}
    if type(l1) is dict:
        l1 = list(l1.keys())
        l2 = list(l2.keys())
    return list(set(l1).difference(set(l2)))


def diff_set_num(l1, l2):
    """diff_set方法用于差集数量

    Parameters
    ----------
    l1 : list or set or dict
        列表1
    l2 : list or set or dict
        列表2

    Returns
    ----------
    """
    assert type(l1) in {list, set, dict}
    assert type(l2) in {list, set, dict}
    if type(l1) is dict:
        l1 = list(l1.keys())
        l2 = list(l2.keys())
    return len(set(l1).difference(set(l2)))


def union_set(l1, l2):
    """union_set方法用于并集

    Parameters
    ----------
    l1 : list or set or dict
        列表1
    l2 : list or set or dict
        列表2

    Returns
    ----------
    """
    assert type(l1) in {list, set, dict}
    assert type(l2) in {list, set, dict}
    if type(l1) is dict:
        l1 = list(l1.keys())
        l2 = list(l2.keys())
    return list(set(l1).union(set(l2)))


def union_set_num(l1, l2):
    """union_set_num方法用于并集数量

    Parameters
    ----------
    l1 : list or set or dict
        列表1
    l2 : list or set or dict
        列表2

    Returns
    ----------
    """
    assert type(l1) in {list, set, dict}
    assert type(l2) in {list, set, dict}
    if type(l1) is dict:
        l1 = list(l1.keys())
        l2 = list(l2.keys())
    return len(set(l1).union(set(l2)))


def combin_dic(*args):
    """combin_dic方法用于合并字典

        Parameters
        ----------
        args : object
            两个字典或多个

        Returns
        ----------
    """
    ret = {}
    if len(args) == 1:
        dicts = args[0]
        assert isinstance(dicts, list)  # 断言是个列表
        for _dict in dicts:
            ret = dict(ret, **_dict)
    else:
        for _dict in args:
            assert isinstance(_dict, dict)
        for _dict in args:
            ret = dict(ret, **_dict)
    return ret


def add_dic(dica, dicb):
    """add_dic方法用于字典累加,数字，字符累加

        Parameters
        ----------
        dica : dict
            字典a
        dicb : dict
            字典b

        Returns
        ----------
    """
    dic = {}
    for key in dica:
        if dicb.get(key):
            dic[key] = dica[key] + dicb[key]
        else:
            dic[key] = dica[key]
    for key in dicb:
        if dica.get(key):
            pass
        else:
            dic[key] = dicb[key]
    return dic


def split_list(_list, slice):
    """split_list方法用于分割列表

        Parameters
        ----------
        _list : list
            列表
        slice : int
            拆分块的大小

        Returns
        ----------
    """
    return [_list[i:i + slice] for i in range(0, len(_list), slice)]


def until(y=None, m=None, d=None, H=None, M=None, S=None, logger=None):
    """until方法用于定时任务

        Parameters
        ----------
        y : int
            年
        m : int
            月
        d : int
            日
        H : int
            时
        M : int
            分
        S : int
            秒
        logger : object
            日志

        Returns
        ----------
    """
    import time
    import datetime
    if y:
        y = int(y)
        m = int(m)
        d = int(d)
        H = int(H)
        M = int(M)
        S = int(S)
        try:
            startTime = datetime.datetime(y, m, d, H, M, S)
        except BaseException:
            if logger:
                logger.info('年月日时分秒输入错误')
            print('年月日时分秒输入错误')
            assert 1 == 2
        if startTime < datetime.datetime.now():
            logger.info('开始时间在当前时间之前')
            print('开始时间在当前时间之前')
            assert 2 == 3

        second = (startTime - datetime.datetime.now()).seconds
        minute = second // 60
        second = second % 60
        hour = minute // 60
        minute = minute % 60
        day = hour // 24
        hour = hour % 24

        print('将于%s天%s小时%s分%s秒 后运行' % (day, hour, minute, second))
        if logger:
            logger.info('将于%s天%s小时%s分%s秒 后运行' % (day, hour, minute, second))

        while datetime.datetime.now() < startTime:
            time.sleep(1)
        print('到达预定时间开始运行程序')
        if logger:
            logger.info('到达预定时间开始运行程序')
    else:
        if d or H or M or S:
            if H is None:
                H = 0
            if M is None:
                M = 0
            if S is None:
                S = 0
            seconds = 0
            time_dic = {'day': 86400,
                        'hour': 3600,
                        'min': 60}
            if d:
                seconds = (
                    time_dic['day'] *
                    int(d) +
                    time_dic['hour'] *
                    int(H) +
                    time_dic['min'] *
                    int(M) +
                    int(S))
                print('将于%s天%s小时%s分%s秒 后运行' % (d, H, M, S))
                if logger:
                    logger.info('将于%s天%s小时%s分%s秒 后运行' % (d, H, M, S))
            elif H:
                seconds = (
                    time_dic['hour'] *
                    int(H) +
                    time_dic['min'] *
                    int(M) +
                    int(S))
                print('将于%s小时%s分%s秒 后运行' % (H, M, S))
                if logger:
                    logger.info('将于%s小时%s分%s秒 后运行' % (H, M, S))
            elif M:
                seconds = (time_dic['min'] * int(M) + int(S))
                print('将于%s分%s秒 后运行' % (M, S))
                if logger:
                    logger.info('将于%s分%s秒 后运行' % (M, S))
            else:
                seconds = int(S)
                print('将于%s秒 后运行' % S)
                if logger:
                    logger.info('将于%s秒 后运行' % S)
            time.sleep(seconds)
            print('到达预定时间开始运行程序')
            if logger:
                logger.info('到达预定时间开始运行程序')
        else:
            print('错误！ 定时任务没有指定时间')
            if logger is not None:
                logger.info('错误！ 定时任务没有指定时间')
                assert 3 == 4


def read(path, sep='\n', encoding='UTF-8'):
    """read方法用于按行读数据

        Parameters
        ----------
        path : str
            路径
        sep : str
            分隔符
        encoding : str
            编码
        Returns
        ----------
    """
    try:
        with open(path, 'r', encoding=encoding) as f:
            return f.read().strip().split(sep)
    except:
        with open(path, 'r') as f:
            return f.read().strip().split(sep)


def write(data, path, sep='\n', encoding='UTF-8'):
    """write方法用于写数据

    Parameters
    ----------
    data : list
        列表数据
    path : str
        存储路径
    sep : str
        分隔符
    encoding : str
        编码种类

    Returns
    ----------
    """
    try:
        with open(path, 'w', encoding=encoding) as f:
            f.write(sep.join(data))
    except:
        with open(path, 'w') as f:
            f.write(sep.join(data))


def merge_commelement_list(lsts):
    """merge_commelement_list方法用于把公共元素的列表合并，返回合并后的结果list

    Parameters
    ----------
    lsts : list
        列表数据
    Returns
    ----------
    """

    sets = [set(lst) for lst in lsts if lst]
    merged = 1
    while merged:
        merged = 0
        results = []
        while sets:
            common, rest = sets[0], sets[1:]
            sets = []
            for x in rest:
                if x.isdisjoint(common):
                    sets.append(x)
                else:
                    merged = 1
                    common |= x
            results.append(common)
        sets = results
    return sets


def flatten(data):
    """flatten方法用于平铺list

    Parameters
    ----------
    data : list
        列表

    Returns
    ----------
    """
    import itertools
    return list(itertools.chain.from_iterable(data))


def read_json(path, encoding='UTF-8'):
    """read_json方法用于读取json文件

    Parameters
    ----------
    path : str
        json文件路径
    encoding : str
        编码类型
    Returns
    ----------
    """
    import json
    try:
        with open(path, 'r', encoding=encoding) as f:
            data = json.loads(f.read())
    except:
        with open(path, 'r') as f:
            data = json.loads(f.read())
    return data


def write_json(data, path, sort=False, encoding='UTF-8'):
    """write_json方法用于写json到文件中

    Parameters
    ----------
    data : str
        字典文件
    path : str
        保存路径
    sort : bool
        是否排序
    encoding : str
        编码类型
    Returns
    ----------
    """
    import json
    try:
        with open(path, "w", encoding=encoding) as f:
            f.write(json.dumps(data, indent=4, ensure_ascii=False, sort_keys=sort))
    except:
        with open(path, "w") as f:
            f.write(json.dumps(data, indent=4, ensure_ascii=False, sort_keys=sort))


def lists_compare(l1, l2):
    """lists_compare方法用于比较两个列表差异性

    Parameters
    ----------
    l1 : list
        列表1
    l2 : list
        列表2

    Returns
    ----------
    """
    dif12 = diff_set(l1, l2)
    dif12_num = len(dif12)
    dif21 = diff_set(l2, l1)
    dif21_num = len(dif21)
    inter = inter_set(l1, l2)
    inter_num = len(inter)
    union = union_set(l1, l2)
    union_num = len(union)
    print('l1 与 l2 差集个数%s' % dif12_num)
    print('l2 与 l1 差集个数%s' % dif21_num)
    print('l2 与 l1 交集个数%s' % inter_num)
    print('l2 与 l1 并集个数%s' % union_num)
    return dif12_num, dif21_num, inter_num, union_num, dif12, dif21, inter, union_num


def iou(l1, l2):
    """iou方法用于计算交集/并集

    Parameters
    ----------
    l1 : list
        列表1
    l2 : list
        列表2

    Returns
    ----------
    """
    inter = inter_set(l1, l2)
    union = union_set(l1, l2)
    if len(union) == 0:
        return 0
    return len(inter)/len(union)


def list_to_dict(_list):
    """list_to_dict方法用于列表转化为字典[[key, val, val], [key, val, val]]

    Parameters
    ----------
    _list : list
        列表

    Returns
    ----------
    """
    from collections import defaultdict
    check = [item[0] for item in _list]  # 查看首元素是否有重复
    if len(check) == len(set(check)):
        _dict = {}
        for item in _list:
            key = item[0]
            item = item[1:]
            item = item[0] if len(item) == 1 else item
            _dict[key] = item
    else:
        _dict = defaultdict(list)
        for item in _list:
            key = item[0]
            item = item[1:]
            _dict[key].extend(item)
    return _dict


def dict_to_list(_dict):
    """dict_to_list方法用于字典转列表

    Parameters
    ----------
    _dict : dict
        字典

    Returns
    ----------
    """
    ret = []
    for key in _dict:
        data = _dict[key]
        if type(data) is list:
            ret.append([key, *data])
        else:
            ret.append([key, data])
    return ret


# def write_yaml(data, path, encoding='UTF-8'):
#     """write_yaml方法用于写yaml配置文件
#
#     Parameters
#     ----------
#     data : dict
#         配置字典
#     path : str
#         保存路径
#     encoding : str
#         编码规则
#
#     Returns
#     ----------
#     """
#     import yaml
#     try:
#         with open(path, 'w', encoding=encoding) as yaml_file:
#             yaml.safe_dump(data, yaml_file)
#     except:
#         with open(path, 'w') as yaml_file:
#             yaml.safe_dump(data, yaml_file)
#
#
# def load_yaml(path, encoding='UTF-8'):
#     """read_yaml方法用于读取yaml文件
#
#     Parameters
#     ----------
#     path : str
#         yaml文件路径
#     encoding : str
#         编码规则
#
#     Returns
#     ----------
#     """
#     import yaml
#     try:
#         with open(path, 'r', encoding=encoding) as f:
#             config = yaml.load(f.read(), Loader=yaml.FullLoader)
#     except:
#         with open(path, 'r') as f:
#             config = yaml.load(f.read())
#     return config


def show_memory(data, suffix='B'):
    """show_memory方法用于查看变量占用内存多少

    Parameters
    ----------
    data: object
        数据对象
    suffix: str
        后缀
        
    Returns
    ----------
    """
    num = sys.getsizeof(data)
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Yi', suffix)


def get_pid():
    """get_pid方法用于当前进程id
    """
    return os.getpid()
