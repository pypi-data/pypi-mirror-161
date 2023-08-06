#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/4/24 11:04
# @Author  : xgy
# @Site    : 
# @File    : cli_all.py
# @Software: PyCharm
# @python version: 3.7.4
"""
from csp.command.cli import csptools

# datatool 命令引入
from csp.datatool.datatool_cli import datatool

# dataset 命令引入
from csp.dataset.dataset_cli import dataset

# resource 命令引入
from csp.resource.resources_cli import resources

# unst2st
from csp.thirdparty.unst2st.unst2st_cli import unst2st

# ocr
from csp.thirdparty.ocr.ocr_cli import ocr

if __name__ == '__main__':
    print("start")
