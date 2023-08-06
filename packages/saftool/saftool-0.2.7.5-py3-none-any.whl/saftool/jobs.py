# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     jobs
   Description :
   Author :        Asdil
   date：          2021/3/31
-------------------------------------------------
   Change Activity:
                   2021/3/31:
-------------------------------------------------
"""
__author__ = 'Asdil'
import joblib
import tempfile
from tqdm import tqdm
from saftool import fo
from saftool import tool


def dump(py_object, save_path, compress=3):
    """dump方法用于持久化python数据

    Parameters
    ----------
    py_object : object
        python 变量
    save_path : str
        存储地址
    compress : int
        压缩率默认3, 数值越高压缩比越大

    Returns
    ----------
    """
    joblib.dump(py_object, save_path, compress=compress)
    print(f'{save_path} 保存成功！')


def load(file_path):
    """load方法用于读取持久化文件

    Parameters
    ----------
    file_path : str
        文件路径

    Returns
    ----------
    读取的二进制文件
    """
    assert fo.is_exist(file_path), f'{file_path} 文件不存在!'
    obj = joblib.load(file_path)
    return obj


def parallel(args, func, njobs, backend=0, verbose=1):
    """parallel方法用于并行计算

    Parameters
    ----------
    args : list
        参数列表
    func : funcion
        对象函数
    njobs : int
        并行数
    backend : int
        并行任务种类
        0: loky 默认
        1: multiprocessing 多进程，鲁棒性不如loky
        2: threading 多线程, 当释放GIL效率高
    verbose : int
        是否输出进度条
    Returns
    ----------
    """
    # 并行种类
    backend_dict = {0: 'loky', 1: 'multiprocessing', 2: 'threading'}
    backend = backend_dict[backend]
    if verbose == 0:
        ret = joblib.Parallel(
            n_jobs=njobs, backend=backend, verbose=0)(
            joblib.delayed(func)(arg) for arg in args)
    else:
        ret = joblib.Parallel(
            n_jobs=njobs, backend=backend, verbose=0)(
            joblib.delayed(func)(arg) for arg in tqdm(args))
    return ret


def memmap(data, path='/tmp/'):
    """memmap方法用于参数共享内存的变量

    Parameters
    ----------
    data : object
        python变量
    path : str
        文件路径
    Returns
    ----------
    内存共享的变量
    """
    tmp_path = tool.path_join(path, 'joblib.mmap')
    if fo.is_exist(tmp_path):  # 若存在则删除
        fo.del_file(tmp_path)
    _ = joblib.dump(data, tmp_path)
    memmap_data = joblib.load(tmp_path, mmap_mode='r+')
    return memmap_data


def load_memmap(path):
    """load_memmap方法用于读取共享数据

    Parameters
    ----------
    path : str
        文件路径

    Returns
    ----------
    """
    memmap_data = joblib.load(path, mmap_mode='r+')
    return memmap_data


def dump_tmp(py_object, file_name):
    """dump_tmp方法用于新建临时文件夹存储数据

    Parameters
    ----------
    py_object : object
        数据对象
    file_name : str
        文件名
    Returns
    ----------
    """
    tmp_folder = tempfile.mkdtemp()
    tmp_path = tool.path_join(tmp_folder, file_name)
    if fo.is_exist(tmp_path):  # 若存在则删除
        fo.del_file(tmp_path)
    _ = joblib.dump(py_object, tmp_path)
    return tmp_path
