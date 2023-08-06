#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/6/8 09:21
# @Author  : liny
# @Site    :
# @File    : ocr_cli.py
# @Software: IDEA
# @python version: 3.7.4
"""

import click
from csp.command.cli import csptools
from csp.thirdparty import Ocr


# 一级命令 CSP ocr
@csptools.group("ocr")
def ocr():
    """
    CSP ocr Command line
    """


## 纯文本抽取
@ocr.command()
@click.option("-v", "--version", help="the version of server images", default=None)
@click.option("-p", "--port", help="the port for server container", default=None)
@click.option("-c", "--c_name", help="the container name", default=None)
@click.option('-r', is_flag=True, help="Re query image information.Indicates true when it appears")
@click.option("-i", "--file", help="the input file", required=True)
def ocr_text(version, port, c_name, r, file):
    """
    OCR plain text extraction
    """
    ocrclient = Ocr(version, port, c_name, reload=r);
    result = ocrclient.ocr_text(file)
    print(result)

## OCR表格识别
@ocr.command()
@click.option("-v", "--version", help="the version of server images", default=None)
@click.option("-p", "--port", help="the port for server container", default=None)
@click.option("-c", "--c_name", help="the container name", required=True, default=None)
@click.option('-r', is_flag=True, help="Re query image information.Indicates true when it appears")
@click.option("-i", "--file", help="the input file", required=True)
def ocr_table(version, port, c_name, r, file):
    """
    OCR table recognition
    """
    ocrclient = Ocr(version=version, port=port, c_name=c_name, reload=r);
    result = ocrclient.ocr_table(file)
    print(result)

## OCR固定格式的电子证照识别
@ocr.command()
@click.option("-v", "--version", help="the version of server images", default=None)
@click.option("-p", "--port", help="the port for server container", default=None)
@click.option("-c", "--c_name", help="the container name",  default=None)
@click.option('-r', is_flag=True, help="Re query image information.Indicates true when it appears")
@click.option("-o", "--code", help="format file code,example：idcard/train_ticket/audit/safety_production_license", required=True)
@click.option("-i", "--file", help="the input file", required=True)
def ocr_fixed_file(version, port, c_name, r, code, file):
    """
    OCR fixed format electronic license recognition
    """
    ocrclient = Ocr(version=version, port=port, c_name=c_name, reload=r);
    result = ocrclient.ocr_fixed_file(code, file)
    print(result)


if __name__ == '__main__':
    print("start")
    ocr()
    # name = "yrocr-cpu"
    # version = 1.2
    # port = 28888
    # img_path = "/Users/liny/work/ocr/text.png";
    # ocr_text(version, port, name, True, img_path);
