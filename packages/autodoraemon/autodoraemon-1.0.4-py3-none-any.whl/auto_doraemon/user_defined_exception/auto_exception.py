#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
自动化测试相关的用户自定义异常

@author:zhaojiajun
@file:auto_exception.py
@time:2022/07/12
"""


class TestMethodsFileNotFoundException(Exception):

    def __init__(self, file_path: str):
        super().__init__(self)
        self.file_path = file_path

    def __str__(self):
        return '记录需要执行的测试方法文件不存在{}'.format(self.file_path)


if __name__ == '__main__':
    pass
