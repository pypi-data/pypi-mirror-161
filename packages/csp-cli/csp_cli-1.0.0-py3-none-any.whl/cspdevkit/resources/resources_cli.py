#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/5/18 18:08
# @Author  : xgy
# @Site    : 
# @File    : resource_cli.py
# @Software: PyCharm
# @python version: 3.7.4
"""

import click
from csp.command.cli import csptools
from csp.resource.resource_server import res_get, res_download


# 一级命令 CSPtools resource
@csptools.group("resource")
def resources():
    """
    CSPTools resource Command line \n the tools for resource,such as list and download
    """


## 资源列表查看
@resources.command()
@click.option("-n", "--name", help="the name of resource", default=None)
def list(name):
    """
    CSPTools resource list line
    """
    res_get(name=name, infer_type="list")


## 资源查找
@resources.command()
@click.option("-n", "--name", help="the name of resource", default=None)
@click.option("-r", "--resdir", help="the dir of resource", default=None)
def find(name, resdir):
    """
    CSPTools resource find line
    """
    if not name and not resdir:
        raise NameError("At least one of name(-n) and resdir(-r) is not empty")
    res_get(name=name, res_dir=resdir, infer_type="search")


## 资源详细信息查看
@resources.command()
@click.option("-n", "--name", help="the name of resource. Name must be complete", required=True)
def info(name):
    """
    CSPTools resource info line
    """
    res_get(name=name, infer_type="info")


## 资源下载
@resources.command()
@click.option("-n", "--name", help="the name of resource", required=True)
@click.option("-c", "--charset", help="the encoding method of resource", default="UTF-8")
@click.option("-o", "--output", help="the folder to save dataset", required=True)
def download(name, charset, output):
    """
    CSPTools resource download line
    """
    res_download(name, charset, output)


if __name__ == '__main__':
    print("start")
