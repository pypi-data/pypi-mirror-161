# -*- coding: utf-8 -*-
"""
jf-ext.BasicType.ListExt.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2018-2022 by the Ji Fu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""


def list_to_string(obj):
    """
    >>> list -> string
    :param {List} obj:
    :return {String}:
    """
    if isinstance(obj, list):
        return str(obj)
    return obj
