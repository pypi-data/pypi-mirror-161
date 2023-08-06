#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/3/29 15:22
# @Author  : xgy
# @Site    : 
# @File    : utils.py
# @Software: PyCharm
# @python version: 3.7.4
"""

import subprocess
import shlex

import prettytable
from prettytable import PrettyTable
from textwrap import fill


class RunSys:
    """
    执行 shell 命令
    """

    def __init__(self, command: str = None):
        self.command = command
        self.output = None

    def run_cli(self):
        cmd = shlex.split(self.command)
        try:
            # output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            subprocess.check_call(cmd, stderr=subprocess.STDOUT)
            return True
            # self.output = output.decode()
        except subprocess.CalledProcessError as e:
            # print(traceback.print_exc())
            # print(e)
            return False


def format(data, title_dict: dict):
    x = PrettyTable(hrules=prettytable.ALL)
    x.align = "l"

    res_l = data["data"]

    # table_data = []
    title = []
    for k, v in title_dict.items():
        title.append(k)
    x.field_names = title

    if res_l:
        if isinstance(res_l, list):
            for item in res_l:
                item_l = []
                for k, v in title_dict.items():
                    if item[title_dict[k]]:
                        item_l.append(fill(str(item[title_dict[k]]), width=20))
                    else:
                        item_l.append('')
                x.add_row(item_l)
        if isinstance(res_l, dict):
            item_l = []
            for k, v in title_dict.items():
                if res_l[title_dict[k]]:
                    item_l.append(fill(res_l[title_dict[k]], width=20))
                else:
                    item_l.append('')
            x.add_row(item_l)

    print(x)


if __name__ == '__main__':
    print("start")


