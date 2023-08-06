#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/6/29 16:14
# @Author  : xgy
# @Site    : 
# @File    : eda.py
# @Software: PyCharm
# @python version: 3.7.4
"""

import os
from loguru import logger
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

from csp.datatool.image_classify.utils import ImgClassify


class ImgClassifyEda(ImgClassify):

    def __init__(self, data_dir, output):
        super(ImgClassifyEda, self).__init__(data_dir)
        self.output = output

    def eda(self):

        labels_dict, _, _ = self.get_labels()
        labels_dict_n = {}
        for k, v in labels_dict.items():
            labels_dict_n[str(v)] = k

        labels_dict_count = {}

        with open(self.list_path, "r", encoding="utf-8") as fr:
            anno_l = fr.readlines()

            for item in anno_l:
                categry_id = item.split(" ")[1].replace("\n", "")
                category = labels_dict_n[categry_id]
                labels_dict_count[category] = labels_dict_count.get(category, 0) + 1

        dpi = 15

        # 条形图
        x_index = []
        x_data = []
        y_data = []

        index = 1
        for k, v in labels_dict_count.items():
            x_data.append(k)
            y_data.append(int(v))
            x_index.append(index)
            index += 1
        plt.figure(figsize=(80, 40))
        plt.xlabel('标签', fontsize=80, loc='right')
        plt.ylabel('数量', fontsize=80)
        plt.title('标签数量分布', fontsize=100)
        plt.xticks(x_index, x_data, size=60, rotation=25)
        plt.bar(x_index, y_data, tick_label=x_data, align="center")

        for a, b in zip(x_index, y_data):
            plt.text(a, b + 0.01, b, ha='center', va='bottom', size=100)

        if self.output:
            os.makedirs(self.output, exist_ok=True)
        plt.savefig(os.path.join(self.output, 'category_num.png'), dpi=dpi)
        logger.info("the eda result files saved in {}".format(self.output))


def img_classify_eda(folder, output=None):
    data_eda = ImgClassifyEda(folder, output)
    data_eda.eda()


if __name__ == '__main__':
    print("start")
