#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/4/11 8:57
# @Author  : xgy
# @Site    : 
# @File    : __init__.py.py
# @Software: PyCharm
# @python version: 3.7.4
"""

from csp import common, command, datatool, dataset, resource, thirdparty

from csp.thirdparty.unst2st.Unst2st import Unst2st
from csp.thirdparty.ocr.Ocr import Ocr
from csp.thirdparty.kg.Kg import Kg
from csp.thirdparty.pdfcheck.PdfCheck import PdfCheck
from csp.thirdparty.translate.Translate import Translate
from csp.thirdparty.labeltool.doccano import doccano

if __name__ == '__main__':
    print("start")
