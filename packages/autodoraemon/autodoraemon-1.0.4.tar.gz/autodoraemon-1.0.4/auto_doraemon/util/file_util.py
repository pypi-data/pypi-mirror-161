#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
文件处理模块

@author:zhaojiajun
@file:file_util.py
@time:2022/07/11
"""
import os
from auto_doraemon.user_defined_exception.auto_exception import TestMethodsFileNotFoundException


def write_file(file_path: str, file_name: str, content: str):
    """
    想文件中写入指定内容
    写入内容之前，如果文件已经存在，会先删除并重新创建文件
    :param file_path:文件路径
    :param file_name:文件名字
    :param content:内容
    :return:
    """
    if not os.path.exists(file_path):
        os.makedirs(file_path, exist_ok=True)
    path = os.path.join(file_path, file_name)
    if os.path.exists(path):
        os.remove(path)
    with open(path, 'w+') as file:
        file.write(content)


def read_file(file_path: str):
    """
    读取文件中的内容
    :param file_path: 文件路径
    :return:
    """
    if not os.path.isfile(file_path) and not os.path.exists(file_path):
        raise TestMethodsFileNotFoundException(file_path)
    with open(file_path, 'r') as file:
        content = file.read()
    return content


if __name__ == '__main__':
    write_file('', 'test.json', '1234')
