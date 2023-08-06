#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
json 处理工具

@author:zhaojiajun
@file:json_util.py
@time:2022/07/28
"""

from deepdiff import DeepDiff, grep

global ignore_value_path_list
ignore_value_path_list = []

global ignore_path_list
ignore_path_list = []

IGNORE_VALUE_STR = "${__ignore_value__}"
IGNORE_STR = "{__ignore__}"


def filter_removed_item(src, tar):
    """
    使用tar对src进行过滤，
    :param src:原始列表
    :param tar:目标列表
    :return: 返回过滤后的列表
    """
    return list(filter(lambda item: item not in src, tar))


def is_same_json(src, tar):
    """
    对比两个json对象

    ${__ignore__}: 在对比时，会忽略此内容的对比，不仅忽略值，而且对应key是否存在都不关系，属于完全忽略
    ${__ignore_value__}: 在对比时，忽略值的不一致，但是key和value必须存在

    :param src:
    :param tar:
    :return: 返回对比结果和对比明细
    """
    global ignore_value_path_list
    global ignore_path_list
    # 查找${__ignore_value__}
    search_result = src | grep(IGNORE_VALUE_STR)
    ignore_value_path_list = search_result['matched_values'] if 'matched_values' in search_result.keys() else []
    # 查找${__ignore__}
    search_result = src | grep(IGNORE_STR)
    ignore_path_list = search_result[
        'matched_values'] if 'matched_values' in search_result.keys() else []

    # 对比，得到对比结果
    detail = DeepDiff(src, tar, exclude_paths=ignore_path_list,
                      ignore_type_in_groups=[DeepDiff.strings, DeepDiff.numbers])

    # 对比结果中的dictionary_item_removed相关内容处理
    # 使用ignore_value_path_list对dictionary_item_removed的结果进行过滤,如果后如果还存在内容，说明存在异常，tar存在缺失
    if detail and "dictionary_item_removed" in detail.keys():
        dictionary_item_removed = detail['dictionary_item_removed']
        filter_result = filter_removed_item(list(filter(lambda item: str(item), dictionary_item_removed)),
                                            ignore_value_path_list)
        if filter_result:
            # 如果过滤后，还存在内容，则重置detail中的dictionary_item_removed内容，剔除了${__ignore_value__}的内容
            detail['dictionary_item_removed'] = filter_result

    # 对比结果中的values_changed相关内容处理
    if detail and "values_changed" in detail.keys():
        ignore_values_changed_list = list(filter(lambda item: item[1]['old_value'] == IGNORE_VALUE_STR,
                                                 detail['values_changed'].items()))
        # 删除掉需要忽略的值变动
        [value for value in
         map(lambda index: detail['values_changed'].pop(index) if detail['values_changed'].get(index) else None,
             [item[0] for item in ignore_values_changed_list])]

    # 对比结果中的type_changes相关内容处理，因为在src中${__ignore_value__}是个字符串，tar中有可能不是字符串，所以这里需要排除
    if detail and "type_changes" in detail.keys():
        ignore_type_changed_list = list(filter(lambda item: item[1]['old_value'] == IGNORE_VALUE_STR,
                                                 detail['type_changes'].items()))
        # 删除掉需要忽略的类型变动
        [value for value in
         map(lambda index: detail['type_changes'].pop(index) if detail['type_changes'].get(index) else None,
             [item[0] for item in ignore_type_changed_list])]

    # 重置结果：清除空的内容
    detail.remove_empty_keys()
    # 返回对比结果
    result = False if detail else True
    return result, detail


if __name__ == '__main__':
    json_1 = {"key1": 123, "key2": "${__ignore__}", "key3": "${__ignore_value__}"}
    json_2 = {"key1": 123, "key2": "test", "key3": 123}

    print(is_same_json(json_1, json_2))
