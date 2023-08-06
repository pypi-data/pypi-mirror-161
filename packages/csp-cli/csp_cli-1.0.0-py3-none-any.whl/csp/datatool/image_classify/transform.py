#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/6/29 15:17
# @Author  : xgy
# @Site    : 
# @File    : transform.py
# @Software: PyCharm
# @python version: 3.7.4
"""

import os
from loguru import logger
import shutil
from csp.datatool.image_classify.utils import ImgClassify


class ImgClassifyTransform(ImgClassify):

    def __init__(self, data_dir, output):
        super(ImgClassifyTransform, self).__init__(data_dir=data_dir)
        self.output = output

    def transform(self):
        labels_dict, _, _ = self.get_labels()
        labels_dict_n = {}
        for k, v in labels_dict.items():
            labels_dict_n[str(v)] = k

        os.makedirs(self.output, exist_ok=True)

        with open(self.list_path, "r", encoding="utf-8") as fr:
            anno_l = fr.readlines()

            for item in anno_l:
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

                item_category = labels_dict_n[item_n.split(" ")[1]]

                category_folder = os.path.join(self.output, item_category)
                os.makedirs(category_folder, exist_ok=True)
                det_img = os.path.join(category_folder, file_name)

                shutil.copy(ori_img, det_img)

        logger.info("the transform result files saved in {}".format(self.output))


def img_classify_transform(folder, output):
    data_transform = ImgClassifyTransform(folder, output)
    data_transform.transform()


if __name__ == '__main__':
    print("start")
