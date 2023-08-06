#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
时间处理工具模块

@author:zhaojiajun
@file:time_util.py
@time:2022/07/12
"""
import time


def get_current_time(time_format: str):
    """
    获取当前时间
    :param time_format: 时间格式
    :return:
    """
    return time.strftime(time_format, time.localtime())


if __name__ == '__main__':
    print(get_current_time())
