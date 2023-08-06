#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/4/24 9:59
# @Author  : xgy
# @Site    : 
# @File    : __init__.py.py
# @Software: PyCharm
# @python version: 3.7.4
"""

# from csp.datatool import image_detection, text_entity
from csp.datatool.dataset.dataset import Dataset

from csp.datatool.APIs import split, transform, check, eva, eda, aug


if __name__ == '__main__':
    print("start")