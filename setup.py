#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'justinfong'

from setuptools import setup, find_packages

setup(
    name='wechat-enterprise-sdk',
    version='0.0.1',
    keywords=('wechat-enterprise', 'wechat enterprise sdk', 'wechat enterprise sdk'),
    description=u'微信企业平台Python开发包',
    long_description="wechat enterprise sdk",
    url='https://github.com/zcfong/wechat_enterprise_sdk',
    packages=find_packages(),
    include_package_data=True,
    install_requires=map(lambda x: x.replace('==', '>='), open("requirements.txt").readlines()),

    test_suite='tests',
)