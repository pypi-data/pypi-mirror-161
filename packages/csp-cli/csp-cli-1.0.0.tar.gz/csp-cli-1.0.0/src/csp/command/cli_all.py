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
from csp.resource.resource_cli import resource

# unst2st
from csp.thirdparty.unst2st.unst2st_cli import unst2st

# ocr
from csp.thirdparty.ocr.ocr_cli import ocr

# kg
from csp.thirdparty.kg.kg_cli import kg

# pdfcheck
from csp.thirdparty.pdfcheck.pdfcheck_cli import pdfcheck

# translate
from csp.thirdparty.translate.translate_cli import translate

# labeltool
from csp.thirdparty.labeltool.labeltool_cli import labeltool

# pipeline
from csp.pipeline.pipeline_cli import pipeline
from csp.pipeline.uiepipe.uie_cli import uie

if __name__ == '__main__':
    print("start")
