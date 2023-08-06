#!/usr/bin/env python
# -*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: thao
# Mail: thao92@126.com
# Created Time:  2020-08-05 11:08:34
#############################################


from setuptools import setup, find_packages
import sys
import importlib

importlib.reload(sys)

setup(
    name="sanydata",
    version="3.0.8",
    keywords=["pip", "sanydata", "thao"],
    description="get data and get wind farm information",
    long_description="get data and get wind farm information",
    license="MIT Licence",

    url="http://gitlab.sanywind.net/sanydata/sanydata",
    author="thao",
    author_email="thao92@126.com",
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=['grpcio', 'grpcio-tools', 'gql', 'pandas', 'elasticsearch',
                      'requests', 'requests_toolbelt', 'cos-python-sdk-v5', 'pyarrow', 'hdfs']
)
