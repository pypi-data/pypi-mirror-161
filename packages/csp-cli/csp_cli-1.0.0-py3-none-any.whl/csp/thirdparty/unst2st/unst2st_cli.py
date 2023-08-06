#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/5/27 15:25
# @Author  : xgy
# @Site    : 
# @File    : unst2st_cli.py
# @Software: PyCharm
# @python version: 3.7.4
"""

import click
from csp.command.cli import csptools
from csp.thirdparty import Unst2st


# 一级命令 CSPtools unst2st
@csptools.group("unst2st")
def unst2st():
    """
    csp unst2st Command line
    """


## 纯文本抽取
@unst2st.command()
@click.option("-v", "--version", help="the version of server images", default=None)
@click.option("-p", "--port", help="the port for server container", default=None)
@click.option("-c", "--c_name", help="the container name", default=None)
@click.option('-r', is_flag=True, help="Re query image information.Indicates true when it appears")
@click.option("-i", "--file", help="the input file", required=True)
@click.option("-o", "--output", help="the folder to save output txt file", default=None)
def extract_text(version, port, c_name, r, file, output):
    """
    csp unst2st extract_text line
    """
    unst2st = Unst2st(version=version, port=port, c_name=c_name, reload=r)
    result = unst2st.extract_text(file, output)
    print(result)


## 去水印
@unst2st.command()
@click.option("-v", "--version", help="the version of server images", default=None)
@click.option("-p", "--port", help="the port for server container", default=None)
@click.option("-c", "--c_name", help="the container name", default=None)
@click.option('-r', is_flag=True, help="Re query image information.Indicates true when it appears")
@click.option("-i", "--in_file", help="the input file", required=True)
@click.option("-o", "--output", help="the output folder", required=True)
def remove_watermark(version, port, c_name, r, in_file, output):
    """
    csp unst2st remove_watermark line
    """
    unst2st = Unst2st(version=version, port=port, c_name=c_name, reload=r)
    unst2st.remove_watermark(in_file, output)

# 抽取图片文本
# @unst2st.command()
# @click.option("-v", "--version", help="the version of server images", required=True)
# @click.option("-p", "--port", help="the port for server container", required=True)
# @click.option("-c", "--c_name", help="the container name", required=True, default=None)
# @click.option('-r', is_flag=True, help="Re query image information.Indicates true when it appears")
# @click.option("-i", "--file", help="the input file", required=True)
# @click.option("-o", "--output", help="the folder to save output txt file", default=None)
# def extract_img_txt(version, port, c_name, r, file, output):
#     """
#     CSPTools unst2st extract_img_txt line
#     """
#     unst2st = Unst2st(version=version, port=port, c_name=c_name, reload=r)
#     result = unst2st.extract_img_txt(file, output)
#     print(result)

# 表格提取
@unst2st.command()
@click.option("-v", "--version", help="the version of server images", default=None)
@click.option("-p", "--port", help="the port for server container", default=None)
@click.option("-c", "--c_name", help="the container name",  default=None)
@click.option('-r', is_flag=True, help="Re query image information.Indicates true when it appears")
@click.option("-i", "--file", help="the input file", required=True)
@click.option("-o", "--output", help="the folder to save output txt file", default=None)
def extract_table(version, port, c_name, r, file, output):
    """
    csp unst2st extract_table line
    """
    unst2st = Unst2st(version=version, port=port, c_name=c_name, reload=r)
    result = unst2st.extract_table(file, output)
    print(result)

# 篇章段落提取
# @unst2st.command()
# @click.option("-v", "--version", help="the version of server images", default=None)
# @click.option("-p", "--port", help="the port for server container", default=None)
# @click.option("-c", "--c_name", help="the container name", default=None)
# @click.option('-r', is_flag=True, help="Re query image information.Indicates true when it appears")
# @click.option("-i", "--file", help="the input file", required=True)
# @click.option("-o", "--output", help="the folder to save output txt file", default=None)
# def extract_structure(version, port, c_name, r, file, output):
#     """
#     csp unst2st extract_structure line
#     """
#     unst2st = Unst2st(version=version, port=port, c_name=c_name, reload=r)
#     result = unst2st.extract_structure(file, output)
#     print(result)


if __name__ == '__main__':
    print("start")
