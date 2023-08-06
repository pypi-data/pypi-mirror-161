#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


def update_current_version():
    # try:
    #     fp = open('version', 'r')
    #     [major, sub, rev] = fp.read().split('.')
    #     version = '{}.{}.{}'.format(major, sub, str(int(rev) + 1))
    #     fp.close()
    #     fp = open('version', 'w')
    #     fp.write(version)
    #     return version
    # except Exception:
    #     return "1.0.0"
    return "1.2.3"


setup(
    name='jfExt',
    version=update_current_version(),
    description='private common python framework',
    long_description='...',
    keywords='jfExt',
    author='jifu',
    author_email='ji.fu@icloud.com',
    url='http://www.jifu.io',
    license='MIT',
    packages=find_packages(exclude=["test", '*.pyc']),
    install_requires=[
        'flask', 'flask_mail', 'flask_redis',
        'six', 'prettytable', 'requests',
        'uuid', 'validators', 'geoip2',
        'icecream', 'urllib3'
    ],
    extras_require={
    },
    package_data={},
    include_package_data=True,
    zip_safe=True,
)
