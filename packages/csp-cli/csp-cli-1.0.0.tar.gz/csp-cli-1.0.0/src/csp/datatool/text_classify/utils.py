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
import json
import os
from csp.datatool.utils import JsonLoad


class TextClassify:

    """
    文本分类数据集
    """

    def __init__(self, data_dir):
        self.data_dir = data_dir

        self.labels_path = os.path.join(self.data_dir, "labels.json")
        self.sources_path = os.path.join(self.data_dir, "sources.json")
        self.category_path = os.path.join(self.data_dir, "labelCategories.json")

        self.label_categories_data = None
        self.labels_data = None
        self.sources_data = None

        self.src_ids = []
        self.cate_ids = []

    def get_categories(self):
        category_dict = {}

        with open(self.category_path, "r", encoding="utf-8") as fr:
            category_l = json.load(fr)
            for item in category_l:
                category_dict[item["id"]] = item["text"]

        self.category_dict = category_dict

        return category_dict

    def get_dataset(self):

        self.label_categories_data = JsonLoad(self.category_path).data
        self.labels_data = JsonLoad(self.labels_path).data
        self.sources_data = JsonLoad(self.category_path).data

    def get_sources_ids(self):
        for item in self.sources_data:
            self.src_ids.append(item["id"])

    def get_cate_ids(self):
        for item in self.label_categories_data:
            self.cate_ids.append(item["id"])




if __name__ == '__main__':
    print("start")
