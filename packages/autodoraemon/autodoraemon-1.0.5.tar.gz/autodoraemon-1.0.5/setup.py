#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
打包模块
@author:zhaojiajun
@file:setup.py
@time:2022/07/11
"""

from setuptools import setup, find_packages

__version__ = '1.0.5'
__name__ = 'autodoraemon'

require_packages = [
    "setuptools==47.1.0",
    "requests==2.25.1",
    "xlrd==2.0.1",
    "deepdiff==5.8.1"
]

setup(
    name=__name__,
    version=__version__,
    description='自动化测试辅助测试项目，主要提供工具函数',
    author='zhaojiajun',
    author_email='zhaojiajun@baicizhan.com',
    packages=find_packages(),
    install_requires=require_packages
)
