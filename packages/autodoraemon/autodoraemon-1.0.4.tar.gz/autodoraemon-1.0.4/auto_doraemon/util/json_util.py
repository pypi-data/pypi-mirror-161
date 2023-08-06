#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
json 处理工具

@author:zhaojiajun
@file:json_util.py
@time:2022/07/28
"""

from deepdiff import DeepDiff, grep


def is_same_json(src, tar):
    """
    对比两个json对象
    :param src:
    :param tar:
    :return: 返回对比结果和对比明细
    """
    # 查找需要忽略对比的内容
    search_result = src | grep("${__ignore__}")
    detail = DeepDiff(src, tar, exclude_paths=search_result['matched_values'])
    result = False if detail else True
    return result, detail


if __name__ == '__main__':
    json_1 = {"key1": 123, "key2": "${__ignore__}"}
    json_2 = {"key1": 123, "key2": "test"}
    print(is_same_json(json_1, json_2))
