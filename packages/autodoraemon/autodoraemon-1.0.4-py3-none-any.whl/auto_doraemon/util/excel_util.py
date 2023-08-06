#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
excel xls 文件读取
@author:zhaojiajun
@file:excel_util.py
@time:2022/07/27
"""
import sys

import xlrd
import os


def read_xls(file_path, sheet_name) -> []:
    """
    读取.xls文件
    此函数将文件中每行内容转成字典，字典的key是列名，放于字典中
    :param file_path:
    :param sheet_name
    :return:
    """
    data = []
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return []
        book = xlrd.open_workbook(file_path)
        # 检查sheet是否存在
        if sheet_name not in book.sheet_names():
            return []
        sheet = book.sheet_by_name(sheet_name)
        rows = sheet.nrows
        columns = sheet.ncols
        for row_index in range(1, rows):
            tmp_dict = {}
            row = sheet.row(row_index)
            for col_index in range(0, columns):
                key = sheet.col_values(col_index, 0, 1)[0]
                value = row[col_index].value
                tmp_dict[key] = value
            data.append(tmp_dict)
    finally:
        return data


if __name__ == '__main__':
    x = read_xls('/Users/zhaojiajun/Desktop/test_auto.xls', 'Sheet1')
    y = 1
