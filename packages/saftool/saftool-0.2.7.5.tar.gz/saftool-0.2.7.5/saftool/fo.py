# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     fo
   Description :   文件相关操作
   Author :        Asdil
   date：          2021/3/31
-------------------------------------------------
   Change Activity:
                   2021/3/31:
-------------------------------------------------
"""
__author__ = 'Asdil'
# 文件操作
import os
import gzip
import py7zr
import shutil
from saftool import tool


def is_dir(path: str) -> bool:
    """is_dir方法用于判断是否是文件夹

    Parameters
    ----------
    path : str
        路径
    Returns
    ----------
    """
    return os.path.isdir(path)


def is_file(path: str) -> bool:
    """is_file方法用于是否是文件

    Parameters
    ----------
    path : str
        文件路径

    Returns
    ----------
    """
    return os.path.isfile(path)


def is_exist(path: str) -> bool:
    """is_exist方法用于是否存在该文件

    Parameters
    ----------
    path : str
        文件路径

    Returns
    ----------
    """
    return os.path.exists(path)


def del_file(path: str) -> bool:
    """del_file方法用于删除文件

    Parameters
    ----------
    path : str
        文件路径

    Returns
    ----------
    """
    if os.path.exists(path):
        os.remove(path)
        return True
    return False


def del_dir(path: str) -> bool:
    """del_dir方法用于删除文件夹

    Parameters
    ----------
    path : str
        文件路径

    Returns
    ----------
    """
    flag = True
    try:
        shutil.rmtree(path)
    except:
        flag = False
    return flag


def del_all_files(path: str, key: [str, None] = None) -> bool:
    """del_all_files方法用于删除目录下所有文件

    Parameters
    ----------
    path : str
        文件路径
    key : str or None
        文件后缀

    Returns
    ----------
    """
    if key is None:
        files = tool.get_files(path)
    else:
        files = tool.get_files(path, extension=key)
    for _file in files:
        if is_file(_file):
            del_file(_file)
        else:
            del_dir(_file)
    return True


def copy_all_files(src_file: str, dst_file: str, key: [str, None] = None, is_replace: bool = False) -> None:
    """copy_all_files方法用于拷贝目录下所有文件

    Parameters
    ----------
    src_file : str
        文件夹路径
    dst_file : str
        目标文件夹路径
    key : str or None
        文件后缀
    is_replace : bool
        是否覆盖
    Returns
    ----------
    """
    if key is None:
        files = tool.get_files(src_file)
    else:
        files = tool.get_files(src_file, extension=key)
    if is_replace:
        for _file in files:
            if is_file(_file):
                _, _, _, name = tool.split_path(_file)
                if is_exist(_file):
                    del_file(tool.path_join(dst_file, name))
                copy_file(_file, dst_file)
            else:
                _, _, _, name = tool.split_path(_file)
                if is_exist(_file):
                    del_dir(tool.path_join(dst_file, name))
                shutil.copytree(_file, dst_file + f'/{name}')
    else:
        for _file in files:
            if is_file(_file):
                copy_file(_file, dst_file)
            else:
                _, _, _, name = tool.split_path(_file)
                shutil.copytree(_file, dst_file + f'/{name}')


def cut_all_files(src_file: str, dst_file: str, key: [str, None] = None, is_replace: bool = False) -> None:
    """cut_all_files方法用于

    Parameters
    ----------
    src_file : str
        文件夹路径
    dst_file : str
        目标文件夹路径
    key : str or None
        文件后缀
    is_replace : bool
        是否覆盖
    Returns
    ----------
    """
    if key is None:
        files = tool.get_files(src_file)
    else:
        files = tool.get_files(src_file, extension=key)
    if is_replace:
        for _file in files:
            if is_file(_file):
                _, _, _, name = tool.split_path(_file)
                if is_exist(_file):
                    del_file(tool.path_join(dst_file, name))
                cut_file(_file, dst_file)
            else:
                _, _, _, name = tool.split_path(_file)
                if is_exist(_file):
                    del_dir(tool.path_join(dst_file, name))
                shutil.move(_file, dst_file + f'/{name}')
                print(f'copy {_file} -> dst_file/{name}')
    else:
        for _file in files:
            if is_file(_file):
                cut_file(_file, dst_file)
            else:
                _, _, _, name = tool.split_path(_file)
                shutil.move(_file, dst_file + f'/{name}')
                print(f'copy {_file} ->> dst_file/{name}')


def copy_file(src_file: str, dst_file:str) -> None:
    """
    复制文件
    :param src_file: 拷贝文件路径
    :param dst_file: 目标路径
    :return:
    """

    if not os.path.isfile(src_file):
        print("%s not exist!" % src_file)
        assert os.path.isfile(src_file) is True
    else:
        _, _, _, name = tool.split_path(src_file)
        if dst_file[-len(name):] == name:
            fpath, fname = os.path.split(dst_file)  # 分离文件名和路径
        else:
            fpath = dst_file

        if not os.path.exists(fpath):
            os.makedirs(fpath)  # 创建路径

        dst_file = tool.path_join(fpath, name)
        shutil.copyfile(src_file, dst_file)  # 复制文件
        print("copy %s -> %s" % (src_file, dst_file))


def cut_file(src_file:str, dst_file:str) -> None:
    """
    剪切文件
    :param src_file: 剪切文件路径
    :param dst_file: 目标路径
    :return:
    """
    if not os.path.isfile(src_file):
        print("%s not exist!" % src_file)
        assert os.path.isfile(src_file) is True
    else:
        fpath, fname = os.path.split(dst_file)    # 分离文件名和路径
        if not os.path.exists(fpath):
            os.makedirs(fpath)                 # 创建路径
        shutil.move(src_file, dst_file)          # 复制文件
        print("cut %s -> %s" % (src_file, dst_file))


def zip_file(file_path: str, out_dir: [str, None] = None, rename: str = None,
             level=1, is_del: bool = False) -> None:
    """zip_file方法用于压缩文件

    Parameters
    ----------
    file_path : str
        文件绝对路径
    out_dir : str or None
        是否输入到其它文件夹
    rename : str or None
        重命名
    level : int
        压缩等级
        0 ZIP_STOREED：只是作为一种存储，实际上并未压缩
        1 ZIP_DEFLATED：用的是gzip压缩算法
        2 ZIP_BZIP2：用的是bzip2压缩算法
        3 ZIP_LZMA：用的是lzma压缩算法
    is_del : bool
        是否删除原文件
    Returns
    ----------
    """
    import zipfile
    # 拆分成文件路径，文件
    dir, name, _, name_extension = tool.split_path(file_path)
    if rename is None:
        rename = name

    if out_dir is None:
        out_dir = dir

    out_path = tool.path_join(out_dir, rename + '.zip')
    azip = zipfile.ZipFile(out_path, 'w')
    # 写入zip
    if level == 0:
        azip.write(file_path, name_extension, compress_type=zipfile.ZIP_STORED)
    elif level == 1:
        azip.write(file_path, name_extension, compress_type=zipfile.ZIP_DEFLATED)
    elif level == 2:
        azip.write(file_path, name_extension, compress_type=zipfile.ZIP_BZIP2)
    else:
        azip.write(file_path, name_extension, compress_type=zipfile.ZIP_LZMA)
    azip.close()
    if is_del:
        os.remove(file_path)
    print(f"zip {file_path} ->> {out_path}")


def unzip_file(file_path: str, out_dir: [str, None] = None, pwd: [str, None] = None, is_del: bool = False) -> None:
    """unzip_file方法用于解压文件

    Parameters
    ----------
    file_path: str
        文件路径
    out_dir: str or None
        输出文件路径
    pwd: str or None
        密码
    is_del: bool
        删除源文件
    Returns
    ----------
    """
    import zipfile
    dir, name, _, name_extension = tool.split_path(file_path)
    azip = zipfile.ZipFile(file_path)
    if pwd:
        azip.setpassword(pwd.encode())
    if out_dir is None:
        azip.extractall(path=dir)
        output = tool.path_join(dir, name)
    else:
        azip.extractall(path=out_dir)
        output = tool.path_join(out_dir, name)
    azip.close()
    if is_del:
        os.remove(file_path)
    print(f"unzip {file_path} ->> {output}")


def gzip_file(file_path: str, out_dir: [str, None] = None, rename: str = None, is_del: bool = False) -> None:
    """gzip_file方法用于压缩文件变为gz

    Parameters
    ----------
    file_path : str
        文件绝对路径
    out_dir : str or None
        是否输入到其它文件夹
    rename : str or None
        重命名
    is_del : bool
        是否删除原文件
    Returns
    ----------
    """
    assert os.path.exists(file_path)
    dir, name, _, name_extension = tool.split_path(file_path)
    if rename is None:
        rename = name
    if out_dir is None:
        out_dir = dir
    rename += '.gz'
    out_path = tool.path_join(out_dir, rename)
    with open(file_path, 'rb') as f_in:
        with gzip.open(out_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    if is_del:
        os.remove(file_path)
    print('gzip {} ->> {}'.format(file_path, out_path))


def gunzip_file(file_path: str, out_dir: [str, None] = None, rename: str = None, is_del: bool = False):
    """gunzip_file方法用于解压gz文件

        Parameters
        ----------
        file_path : str
            文件绝对路径
        out_dir : str or None
            是否输入到其它文件夹
        rename : str or None
            重命名
        is_del : bool
            是否删除原文件
        Returns
        ----------
        """
    assert os.path.exists(file_path)
    dir, name, _, name_extension = tool.split_path(file_path)
    if rename is None:
        rename = name
    if out_dir is None:
        out_dir = dir
    if rename[-3:] == '.gz':
        rename = rename[:-3]
    out_path = tool.path_join(out_dir, rename)
    with gzip.open(file_path, 'rb') as f_in:
        data = f_in.read().decode('utf8')
        with open(out_path, 'w') as f_out:
            f_out.write(data)
    if is_del:
        os.remove(file_path)
    print('gunzip {} ->> {}'.format(file_path, out_path))


def zip_dir(file_dir: str, out_dir: [str, None] = None, rename: str = None, is_del: bool = False) -> None:
    """zip_dir方法用于压缩文件夹

    Parameters
    ----------
    file_dir : str
        文件夹路径
    out_dir : str or None
        是否输入到其它文件夹
    rename : str or None
        重命名
    is_del : bool
        是否删除原文件

    Returns
    ----------
    """
    dir, name, _, name_extension = tool.split_path(file_dir)
    if rename is None:
        rename = name
    # 压缩文件夹
    if out_dir is None:
        out_path = tool.path_join(dir, rename)
        shutil.make_archive(out_path, 'zip', file_dir)
    else:
        out_path = tool.path_join(out_dir, rename)
        shutil.make_archive(out_path, 'zip', file_dir)
    if is_del:
        os.remove(file_dir)
    print(f"zip {file_dir} ->> {out_path + '.zip'}")


def unzip_dir(file_dir: str, out_dir: [str, None] = None, rename: [str, None] = None) -> None:
    """unzip_dir方法用于解压文件夹

    Parameters
    ----------
    file_dir : str
        文件夹目录
    out_dir : str or None
        输出目录
    rename: str or None
        重命名

    Returns
    ----------
    """
    dir, name, _, _ = tool.split_path(file_dir)
    if out_dir is None:
        out_dir = dir
    if rename is None:
        rename = name
    output = tool.path_join(out_dir, rename)

    shutil.unpack_archive(file_dir, output)
    print(f'unzip {file_dir} ->> {output}')


def zip_7z(file_dir: str, out_dir: [str, None] = None, rename: [str, None] = None,
           pwd: [str, None] = None, speed: int = 3, is_del: bool = False):
    """zip_7z方法用于7zip压缩文件

    Parameters
    ----------
    file_dir: str
        文件或者文件夹路径
    out_dir: str
        输出路径
    rename: str or None
        重命名
    pwd: str or None
        密码
    speed: int
        压缩算法种类
    is_del: bool
        是否删除源文件

    Returns
    ----------
    """
    algorithms = {
        0: [{'id': py7zr.FILTER_ZSTD, 'level': 1}],
        1: [{'id': py7zr.FILTER_ZSTD, 'level': 6}],
        2: [{'id': py7zr.FILTER_ZSTD, 'level': 10}],
        3: [{'id': py7zr.FILTER_DEFLATE}],
        4: [{'id': py7zr.FILTER_BZIP2}],
        5: [{'id': py7zr.FILTER_LZMA2, 'preset': 1}],
        6: [{'id': py7zr.FILTER_LZMA2, 'preset': 10}],
        7: [{'id': py7zr.FILTER_LZMA}]
    }
    if pwd:
        parm = {'id': py7zr.FILTER_CRYPTO_AES256_SHA256}
        algorithms[speed].append(parm)

    dir, name, _, name_extension = tool.split_path(file_dir)
    if rename is None:
        rename = name
    if out_dir is None:
        out_dir = dir
    out_path = tool.path_join(out_dir, rename+'.7z')
    with py7zr.SevenZipFile(out_path, 'w', filters=algorithms[speed], password=pwd) as archive:
        archive.writeall(file_dir, name_extension)
    if is_del:
        if is_file(file_dir):
            del_file(file_dir)
        else:
            del_dir(file_dir)
    print(f'7z {file_dir} ->> {out_path}')
    return True


def unzip_7z(file_dir: str, out_dir: [str, None] = None, pwd: [str, None] = None, is_del: bool = False):
    """unzip_7z方法用于解压7zip

    Parameters
    ----------
    file_dir: str
        文件路径
    out_dir: str
        输出路径
    pwd: str or None
        密码
    is_del: bool
        是否删除源文件

    Returns
    ----------
    """
    dir, name, _, name_extension = tool.split_path(file_dir)

    if out_dir is None:
        out_dir = dir

    with py7zr.SevenZipFile(file_dir, mode='r', password=pwd) as z:
        z.extractall(out_dir)
    if is_del:
        del_file(file_dir)
    print(f'un7z {file_dir}')
    return True


def create_dir(path):
    """create_dir方法用于检查文件夹是否存在，如果存在则删除重新创建

        Parameters
        ----------
        path : str
            文件夹路径

        Returns
        ----------
    """
    if not os.path.exists(path):
        os.makedirs(path)
        return True
    return False


if __name__ == '__main__':
    unzip_dir('/home/asdil/Documents/python/code/1/1.zip')


