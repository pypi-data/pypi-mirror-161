#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/6/28 17:30
# @Author  : xgy
# @Site    : 
# @File    : pdfcheck_cli.py
# @Software: PyCharm
# @python version: 3.7.4
"""

import click
from csp.command.cli import csptools
from csp.thirdparty import PdfCheck


# 一级命令 CSPtools pdfcheck
@csptools.group("pdfcheck")
def pdfcheck():
    """
    csp pdfcheck Command line
    """

## pdf 缺陷检测
@pdfcheck.command()
@click.option("-v", "--version", help="the version of server images", default=None)
@click.option("-p", "--port", help="the port for server container", default=None)
@click.option("-c", "--c_name", help="the container name", default=None)
@click.option('-r', is_flag=True, help="Re query image information.Indicates true when it appears")
@click.option("-i", "--in_file", help="the pdf file name", required=True)
def check(version, port, c_name, r, in_file):
    """
    csp pdfcheck check line
    """
    pdf_check = PdfCheck(version=version, port=port, c_name=c_name, reload=r)
    result = pdf_check.check(in_file)
    print(result)


if __name__ == '__main__':
    print("start")
