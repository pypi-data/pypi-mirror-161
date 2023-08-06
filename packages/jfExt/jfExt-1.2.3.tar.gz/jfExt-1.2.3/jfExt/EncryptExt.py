# -*- coding: utf-8 -*-
"""
jf-ext.EncryptExt.py
~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2018-2022 by the Ji Fu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""

import os
import uuid
import hashlib


def generate_md5(source):
    """
    >>> 加密: 生成Md5值
    :param {String} source: 源字符串
    :return {String}: MD5值
    """
    md5 = hashlib.md5()
    md5.update(source.encode("utf-8"))
    return md5.hexdigest()


def check_md5(source, md5_val):
    """
    >>> 加密: MD5值校验
    :param {String} source: 源字符串
    :param {String} md5_val: MD5值
    :return {Boolean}: MD5值是否匹配
    """
    new_md5_val = generate_md5(source)
    if new_md5_val == md5_val:
        return True
    else:
        return False


def generate_token():
    """
    >>> 加密: 随机生成TOKEN
    :return {String}: MD5 TOKEN
    """
    return hashlib.sha1(os.urandom(24)).hexdigest()


def gen_id():
    """
    >>> 随机成32位字符串
    """
    return uuid.uuid4().hex


def gen_random_id_by_length(length):
    """
    >>> 随机生成定长字符串
    :param {Integer} len: 字符串长度
    """
    return hashlib.sha1(os.urandom(24)).hexdigest()[:length]
