# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     encrypt
   Description :   用于编码转码
   Author :        Asdil
   date：          2021/3/31
-------------------------------------------------
   Change Activity:
                   2021/3/31:
-------------------------------------------------
"""
__author__ = 'Asdil'
import base64
import pickle


def base_encrypt(data):
    """base_encrypt方法用于base64转码

    Parameters
    ----------
    data : str
        需要转码的字符串
    Returns
    ----------
    """
    data = bytes(data, encoding="utf8")
    encrypt_data = base64.b64encode(data)
    encrypt_data = str(encrypt_data, encoding="utf8")
    return encrypt_data


def base_decrypt(data):
    """base_decrypt方法用于base64解码

    Parameters
    ----------
    data : str
        转码后字段

    Returns
    ----------
    """
    data = bytes(data, encoding="utf8")
    decrypt_data = base64.b64decode(data)
    decrypt_data = str(decrypt_data, encoding="utf8")
    return decrypt_data


def encode(data):
    """to_byte方法用于将对象转换为字节

    Parameters
    ----------
    data : object
        任意对象
    Returns
    ----------
    """
    data = base64.b64encode(pickle.dumps(data)).decode("ascii")
    return data


def decode(data):
    """from_byte方法用于将字节对象还原

    Parameters
    ----------
    data : bytearray
        字节数据
    Returns
    ----------
    """
    data = base64.b64decode(data)
    data = pickle.loads(data)
    return data
