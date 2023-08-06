#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: Cai Jianping
# Mail: jpingcai@163.com
# Created Time:  2022-7-9 11:25:34 AM
#############################################


from setuptools import setup, find_packages

setup(
    name = "exCvxpy",
    version = "0.1.2",
    keywords = ("cvxpy","optimization"),
    description = "A cvxpy extension that adds some atomic operations",
    long_description = "A cvxpy extension that adds some atomic operations",
    license = "MIT Licence",

    url = "https://github.com/imcjp/exCvxpy",
    author = "Cai Jianping",
    author_email = "jpingcai@163.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ['cvxpy']
)
