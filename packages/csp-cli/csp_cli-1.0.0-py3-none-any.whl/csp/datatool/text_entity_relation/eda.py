#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/7/1 15:49
# @Author  : xgy
# @Site    : 
# @File    : eda.py
# @Software: PyCharm
# @python version: 3.7.4
"""

import os
import json

from loguru import logger
import matplotlib.pyplot as plt
from csp.datatool.text_entity.eda import EntityEda


plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


class SpoEda(EntityEda):

    def __init__(self, folder, output=None):
        super(SpoEda, self).__init__(folder, output)
        self.output = output
        self.relation_path = os.path.join(self.data_dir, "connections.json")
        self.relationCategories_path = os.path.join(self.data_dir, "connectionCategories.json")

    def eda(self):
        super(SpoEda, self).eda()
        self.eda_relation()

    def eda_relation(self):
        self.load_relation_data()

        relation_dict_count = {}
        for item in self.data_relation:
            category = self.relationCategories_dict[item["categoryId"]]
            relation_dict_count[category] = relation_dict_count.get(category, 0) + 1

        dpi = 15

        # 条形图
        x_index = []
        x_data = []
        y_data = []

        index = 1
        for k, v in relation_dict_count.items():
            x_data.append(k)
            y_data.append(int(v))
            x_index.append(index)
            index += 1
        plt.figure(figsize=(80, 40))
        plt.xlabel('关系', fontsize=80, loc='right')
        plt.ylabel('数量', fontsize=80)
        plt.title('关系数量分布', fontsize=100)
        plt.xticks(x_index, x_data, size=60, rotation=25)
        plt.bar(x_index, y_data, tick_label=x_data, align="center")

        for a, b in zip(x_index, y_data):
            plt.text(a, b + 0.01, b, ha='center', va='bottom', size=100)

        if self.output:
            os.makedirs(self.output, exist_ok=True)
        plt.savefig(os.path.join(self.output, 'connection_num.png'), dpi=dpi)
        logger.info("the eda result files saved in {}".format(self.output))

    def load_relation_data(self):
        with open(self.relation_path, "r", encoding="utf-8") as fr:
            data_relation = json.load(fr)
        with open(self.relationCategories_path, "r", encoding="utf-8") as fr:
            data_relationCategories = json.load(fr)

        relationCategories_dict = {}
        for item in data_relationCategories:
            relationCategories_dict[item["id"]] = item["text"]

        self.data_relation = data_relation
        self.data_relationCategories = data_relationCategories
        self.relationCategories_dict = relationCategories_dict


def spo_eda(data_dir, output):
    # try:
    #     import pandas as pd
    # except ImportError:
    #     logger.error("there is no pandas try to install it, pip install pandas")
    #     install_cmd = "pip install pandas"
    #     RunSys(command=install_cmd).run_cli()

    data_eda = SpoEda(data_dir, output)
    data_eda.eda()


if __name__ == '__main__':
    print("start")
