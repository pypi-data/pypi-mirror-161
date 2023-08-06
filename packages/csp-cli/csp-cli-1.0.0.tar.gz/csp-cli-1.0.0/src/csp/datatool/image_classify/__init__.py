#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/4/24 10:03
# @Author  : xgy
# @Site    : 
# @File    : __init__.py.py
# @Software: PyCharm
# @python version: 3.7.4
"""

from csp.datatool.image_classify.check import img_classify_check
from csp.datatool.image_classify.split import img_classify_split
from csp.datatool.image_classify.transform import img_classify_transform
from csp.datatool.image_classify.eda import img_classify_eda
from csp.datatool.image_classify.aug import img_classify_aug
from csp.datatool.image_classify.eva import img_classify_eva

if __name__ == '__main__':
    print("start")
