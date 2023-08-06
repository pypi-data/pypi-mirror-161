# -*- coding: utf-8 -*-
"""
jf-ext.BasicType.DictExt.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2018-2022 by the Ji Fu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""


def dict_get_and_insert(dic, key, default):
    """
    >>> 字典: 获取字段, 未找到直接插入
    :param {dictionary} dic: 待处理字典
    :param {String} key: 键
    :param {Any} default: 默认插入值
    """
    if not dic.get(key, None):
        dic[key] = default
    return


def dict_flatten(obj):
    """
    >>> 字典拍平
    """
    from jfExt.BasicType.ListExt import list_to_string
    if not isinstance(obj, dict):
        return False
    new_obj = dict()
    for i in obj.keys():
        # 字典类型展开
        if isinstance(obj[i], dict):
            for j in obj[i].keys():
                tmp = list_to_string(obj[i][j])
                new_obj["{}_{}".format(i, j)] = tmp
            continue
        if isinstance(obj[i], list):
            new_obj[i] = list_to_string(obj[i])
            continue
        new_obj[i] = obj[i]
    return new_obj
