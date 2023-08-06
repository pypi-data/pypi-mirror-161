#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/6/21 15:59
# @Author  : xgy
# @Site    : 
# @File    : __init__.py.py
# @Software: PyCharm
# @python version: 3.7.4
"""

from csp.datatool.text_entity_relation.check import spo_check
from csp.datatool.text_entity_relation.split import spo_split
from csp.datatool.text_entity_relation.transform import spo_transform
from csp.datatool.text_entity_relation.spo_eva import spo_eva
from csp.datatool.text_entity_relation.eda import spo_eda

if __name__ == '__main__':
    print("start")
