#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/4/26 15:58
# @Author  : xgy
# @Site    : 
# @File    : split.py
# @Software: PyCharm
# @python version: 3.7.4
"""

import json
import os

from loguru import logger

from csp.datatool.utils import Entity, Filter


class EntitySplit(Entity):

    def __init__(self, folder, output=None):
        super(EntitySplit, self).__init__(folder, output)
        self.output = output if output else self.folder

    def filter_by_scr(self, ratio=0.9):
        self.get_sources_ids()
        size = len(self.src_ids)
        filter = Filter(size)
        index_train = filter.choice_random(ratio=ratio)

        source_train = []
        source_test = []
        test_id = []
        for index, item in enumerate(self.sources_data):
            if index in index_train:
                source_train.append(item)
            else:
                source_test.append(item)
                test_id.append(item["id"])

        label_train = []
        label_test = []
        for label in self.labels_data:
            srcId = label["srcId"]
            if srcId in test_id:
                label_test.append(label)
            else:
                label_train.append(label)

        if self.output:
            output_train = os.path.join(self.output, "train")
            output_val = os.path.join(self.output, "val")
        else:
            output_train = os.path.join(self.folder, "train")
            output_val = os.path.join(self.folder, "val")

        os.makedirs(output_train, exist_ok=True)
        os.makedirs(output_val, exist_ok=True)

        labels_train_path = os.path.join(output_train, "labels.json")
        sources_train_path = os.path.join(output_train, "sources.json")
        labelCategories_train_path = os.path.join(output_train, "labelCategories.json")

        labels_val_path = os.path.join(output_val, "labels.json")
        sources_val_path = os.path.join(output_val, "sources.json")
        labelCategories_test_path = os.path.join(output_val, "labelCategories.json")

        data_dict = {labels_train_path: label_train,
                     sources_train_path: source_train,
                     sources_val_path: source_test,
                     labels_val_path: label_test,
                     labelCategories_train_path: self.label_categories_data,
                     labelCategories_test_path: self.label_categories_data}

        for k, v in data_dict.items():
            # file_name = k + ".json"
            # output_item = os.path.join(self.output, file_name) if self.output else os.path.join(self.folder, file_name)
            # with open(output_item, "w", encoding="utf-8") as f:
            with open(k, "w", encoding="utf-8") as f:
                json.dump(v, f, ensure_ascii=False, indent=4)
            logger.info("the result has been saved in {}".format(k))

        return source_train, source_test


def entity_split(folder, ratio=0.9, output=None):
    filter_entity = EntitySplit(folder, output=output)
    filter_entity.get_dataset()
    filter_entity.filter_by_scr(ratio=ratio)


if __name__ == '__main__':
    print("start")
    # test_dir = "C:/Users/xgy/Desktop/CSPTools/0424/文本实体标注格式"
    # out = "D:/document/pycharmpro/CSPTools/test/output"
    # entity_split(test_dir, output=out)
