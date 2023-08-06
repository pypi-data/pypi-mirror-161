#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/6/29 14:19
# @Author  : xgy
# @Site    : 
# @File    : utils.py
# @Software: PyCharm
# @python version: 3.7.4
"""

import os


class ImgClassify:

    """
    图像分类数据集
    """

    def __init__(self, data_dir):
        self.data_dir = data_dir

        self.labels_path = os.path.join(self.data_dir, "labels.txt")
        self.list_path = os.path.join(self.data_dir, "train_list.txt")
        self.img_dir = os.path.join(self.data_dir, "dateset")

    def get_labels(self):
        labels_dict = {}
        labels_l_n = []
        with open(self.labels_path, "r", encoding="utf-8") as fr:
            labels_l = fr.readlines()
            len_labels = len(labels_l)
            for index, item in enumerate(labels_l):
                labels_dict[item.replace("\n", "")] = index
                labels_l_n.append(item.replace("\n", ""))
        self.len_labels = len_labels
        self.labels_dict = labels_dict
        self.labels = labels_l_n

        return labels_dict, labels_l_n, len_labels



if __name__ == '__main__':
    print("start")
