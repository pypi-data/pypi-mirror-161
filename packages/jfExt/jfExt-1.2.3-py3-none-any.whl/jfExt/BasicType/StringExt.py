# -*- coding: utf-8 -*-
"""
jf-ext.BasicType.StringExt.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2018-2022 by the Ji Fu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""

import random
import difflib


def string_rm_blank(string):
    """
    >>> 替换字符串中空格 -> _
    :param {String} string: 带空格字符串
    :return {String}: 替换后字符串
    """
    return string.replace(" ", "_", 1000)


def string_remove_non_ascii(text):
    """
    >>> 替换字符串中 非ASCII 字符串
    :param {String} text:
    :return {String}:
    """
    return ''.join([i if ord(i) < 128 else " " for i in text])


def string_key_filter(s):
    """
    >>> 过滤wordpress字符中&编码问题
    """
    if isinstance(s, str):
        # s = str(s).replace('&amp;', '&', 100)
        s = str(s).replace('，', ',', 100)
        s = str(s).replace('\\', ',', 100)
    return s


def string_random(str_len):
    """
    随机生成指定长度的字符串
    :param {Int} str_len: 指定长度
    :return {string}:
    """
    res = ''
    for i in range(str_len):
        res += chr(int(random.random() * 100) % 26 + 65)

    return res


def string_similar(s1, s2):
    """
    >>> 字符串相似度计算
    :param {String} s1: 字符串1
    :param {String} s2: 字符串s
    :return {}: 相似度
    """
    return difflib.SequenceMatcher(None, s1, s2).quick_ratio()
