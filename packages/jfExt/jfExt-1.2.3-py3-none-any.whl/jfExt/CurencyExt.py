# -*- coding: utf-8 -*-
"""
jf-ext.CurrencyExt.py
~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2018-2022 by the Ji Fu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""


def currency_display_by_int(number):
    """
    >>> money: 金额 书面化 (千位 ,)
    :param {Int} number: 金额
    :return {String}: 金额书面化字符串
    """
    tmp = format(number, ',')
    return tmp
