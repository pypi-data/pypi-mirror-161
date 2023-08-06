# -*- coding: utf-8 -*-
"""
jf-ext.PrintExt.py
~~~~~~~~~~~~~~~~~~

:copyright: (c) 2018-2022 by the Ji Fu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""

from icecream import ic # noqa:


def print_title(title):
    """
    >>> 打印标题行
    :param {String} title:
    """
    print("")
    print("")
    print(get_color_text_by_style('*' * 50, 0))
    print(get_color_text_by_style(title, 0))
    print(get_color_text_by_style('*' * 50, 0))


def print_sub_title(sub_title):
    """
    >>> 打印小标题行
    :param {String} sub_title:
    """
    print(get_color_text_by_style('-' * 25, 1))
    print(get_color_text_by_style(sub_title, 1))
    print(get_color_text_by_style('-' * 25, 1))


def get_color_text_by_style(text, style):
    """
    >>> 提供带颜色的文字 by style
    :param {Integer} style:
        - 0: 红色字体
    :return {String}:
    """
    if style == 0:
        return "\033[31m{}\033[0m".format(text)
    if style == 1:
        return "\033[32m{}\033[0m".format(text)
