#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/5/18 9:44
# @Author  : xgy
# @Site    : 
# @File    : dataset_cli.py
# @Software: PyCharm
# @python version: 3.7.4
"""

import click
from csp.command.cli import csptools
from csp.dataset.dataset_server import data_download, data_get


# 一级命令 CSPtools dataset
@csptools.group("dataset")
def dataset():
    """
    CSPTools dataset Command line \n the tools for dataset,such as list and download
    """


## 数据集资源展示
@dataset.command()
# @click.option("-n", "--name", help="the name of dataset", default=None)
def list():
    """
    CSPTools dataset list line
    """
    data_get(infer_type="list")


## 数据集资源按名称查找
@dataset.command()
@click.option("-n", "--name", prompt="the name of dataset", help="the name of dataset", required=True)
def find(name):
    """
    CSPTools dataset find line
    """
    data_get(name, infer_type="search")


## 数据集资源按名称展示详细信息
@dataset.command()
@click.option("-n", "--name", prompt="the name of dataset", help="the name of dataset", required=True)
def info(name):
    """
    CSPTools dataset info line
    """
    data_get(name, infer_type="info")


## 数据集资源下载
@dataset.command()
@click.option("-n", "--name", help="the name of dataset", default=None)
@click.option("-m", "--mode", type=click.Choice(['raw', 'train', 'eva']),
              prompt="the mode of dataset", help="the model of dataset", required=True)
@click.option("-s", "--size", help="the size of dataset will be download", default=None)
@click.option("-o", "--output", help="the folder to save dataset", required=True)
def download(name, mode, size, output):
    """
    CSPTools dataset download line
    """
    data_download(name, mode, size, output)


if __name__ == '__main__':
    print("start")
