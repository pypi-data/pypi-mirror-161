#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/6/29 14:05
# @Author  : xgy
# @Site    : 
# @File    : split.py
# @Software: PyCharm
# @python version: 3.7.4
"""

import os
import random
import shutil
from loguru import logger

from csp.datatool.image_classify.utils import ImgClassify


class ImgClassifySplit(ImgClassify):

    def __init__(self, data_dir, output_dir=None, ratio=None):
        super(ImgClassifySplit, self).__init__(data_dir)
        self.data_dir = data_dir
        self.ratio = ratio
        self.output_dir = output_dir if output_dir else data_dir
        self.output_train = os.path.join(self.output_dir, "train")
        self.output_val = os.path.join(self.output_dir, "val")

    def split(self):
        """
        以 train_list.txt 为切分基准
        """
        with open(self.list_path, "r", encoding="utf-8") as fr:
            ann_l = fr.readlines()

        num = len(ann_l)
        list_ids = range(num)

        if not self.ratio:
            self.ratio = 0.9

        len_train = int(num * self.ratio)
        train_l = random.sample(list_ids, len_train)

        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.output_train, exist_ok=True)
        os.makedirs(self.output_val, exist_ok=True)

        train_img_folder = os.path.join(self.output_dir, "train/dataset")
        val_img_folder = os.path.join(self.output_dir, "val/dataset")

        os.makedirs(train_img_folder, exist_ok=True)
        os.makedirs(val_img_folder, exist_ok=True)

        ftrain = open(os.path.join(self.output_train, 'train.txt'), 'w', encoding='utf-8')
        fval = open(os.path.join(self.output_val, 'val.txt'), 'w', encoding='utf-8')

        for i in list_ids:
            item = ann_l[i]
            item_n = item.replace("\n", "")

            # 兼容文件路径分隔符
            if "/" in item and "\\\\" not in item:
                item_split = item_n.split(" ")[0].split("/")
                file_name = item_split[-1]
            elif "/" not in item and "\\\\" in item:
                item_split = item_n.split(" ")[0].split("\\\\")
                file_name = item_split[-1]
            elif "/" in item and "\\\\" in item:
                item_split = item_n.split(" ")[0].split("\\\\")
                if "/" in item_split[-1]:
                    item_split = item_split[-1].split("/")
                    file_name = item_split[-1]
                else:
                    file_name = item_split[-1]
            else:
                file_name = item_n.split(" ")[0].lstrip(".")
            ori_img = os.path.join(self.img_dir, file_name)

            if i in train_l:
                ftrain.write(item)
                # 复制对应图片至训练集
                det_img = os.path.join(train_img_folder, file_name)
                shutil.copy(ori_img, det_img)

            else:
                det_img = os.path.join(val_img_folder, file_name)
                shutil.copy(ori_img, det_img)
                fval.write(item)

        ftrain.close()
        fval.close()

        # 复制labels.txt
        train_labels_path = os.path.join(self.output_train, "labels.txt")
        val_labels_path = os.path.join(self.output_val, "labels.txt")
        shutil.copy(self.labels_path, train_labels_path)
        shutil.copy(self.labels_path, val_labels_path)

        logger.info("the split result files saved in {}".format(self.output_dir))


def img_classify_split(folder, ratio, output=None):
    data_split = ImgClassifySplit(folder, output, ratio)
    data_split.split()


if __name__ == '__main__':
    print("start")
