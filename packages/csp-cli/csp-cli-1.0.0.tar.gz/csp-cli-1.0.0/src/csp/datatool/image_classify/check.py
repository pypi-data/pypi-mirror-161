#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/6/29 9:09
# @Author  : xgy
# @Site    : 
# @File    : check.py
# @Software: PyCharm
# @python version: 3.7.4
"""
import json
import os
import re
from PIL import Image
from loguru import logger

from csp.datatool.image_classify.utils import ImgClassify


class ImgClassifyCheck(ImgClassify):

    """
    图像分类数据集检查
    """

    def __init__(self, data_dir, output_dir):
        super(ImgClassifyCheck, self).__init__(data_dir)
        self.data_dir = data_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def is_img_break(self):
        """
        判断图片是否存在错误，如无法打开
        """
        img_break_txt = os.path.join(self.output_dir, "img_error.txt")
        if os.path.exists(img_break_txt):
            os.remove(img_break_txt)
        flag = True

        error_list = []
        for img in os.listdir(self.img_dir):
            # img_name = os.path.splitext(img)[0]
            img_path = os.path.join(self.img_dir, img)
            file_size = os.path.getsize(img_path)
            file_size = round(file_size / float(1024 * 1024), 2)
            if file_size == 0:
                flag = False
                error_item = {"img_name": img, "message": "the size is zero"}
                error_list.append(error_item)
            else:
                try:
                    img = Image.open(img_path)
                    img.verify()
                except OSError("the img load fail"):
                    flag = False
                    error_item = {"img_name": img, "message": "img load fail"}
                    error_list.append(error_item)

        if not flag:
            # 仅生成 img_error.txt
            with open(img_break_txt, "a+", encoding="utf-8") as fw:
                for item in error_list:
                    fw.write(json.dumps(item, ensure_ascii=False))
                    fw.write("\n")
            logger.info("the error img name has been save to the {}".format(img_break_txt))
        else:
            print("there are no error images")
        return flag

    # def get_labels(self):
    #
    #     labels_dict = {}
    #     labels_l_n = []
    #     with open(self.labels_path, "r", encoding="utf-8") as fr:
    #         labels_l = fr.readlines()
    #         len_labels = len(labels_l)
    #         for index, item in enumerate(labels_l):
    #             labels_dict[item.replace("\n", "")] = index
    #             labels_l_n.append(item.replace("\n", ""))
    #     self.len_labels = len_labels
    #     self.labels_dict = labels_dict
    #     self.labels = labels_l_n
    #
    #     return labels_dict, labels_l_n, len_labels

    def is_anno_break(self):
        """
        判断标注数据是否存在错误
        1.分类结果数值是否超过标签数量
        2.标注文件分类结果数值为空
        3.标注文件标注结果与数据记录之间应存在空格
        """
        self.get_labels()
        anno_break_txt = os.path.join(self.output_dir, "anno_error.txt")
        if os.path.exists(anno_break_txt):
            os.remove(anno_break_txt)

        anno_error_l = []
        with open(self.list_path, "r", encoding="utf-8") as fr:
            anno_l = fr.readlines()
            len_anno = len(anno_l)
            for index, item in enumerate(anno_l):
                item = item.replace("\n", "")
                item_split = item.split(" ")
                if len(item_split) == 1:
                    pattern = r'[0-9]{1,3}$'
                    match_result = re.search(pattern, item_split[0])
                    if match_result:
                        error_item = {"message": "There is no space between file name and label number", "data": item}
                        anno_error_l.append(error_item)
                    else:
                        error_item = {"message": "There is no label number", "data": item}
                        anno_error_l.append(error_item)
                elif len(item_split) == 2:
                    try:
                        item_id = int(item_split[1].replace("\n", ""))
                        if item_id < 0 or item_id > self.len_labels:
                            error_item = {"message": "label number out of range", "data": item}
                            anno_error_l.append(error_item)
                    except Exception:
                        error_item = {"message": "The second column is not a number", "data": item}
                        anno_error_l.append(error_item)
                else:
                    error_item = {"message": "Should be two columns. Space as separator", "data": item}
                    anno_error_l.append(error_item)

        if anno_error_l:
            with open(anno_break_txt, "a+", encoding="utf-8") as fw:
                for item in anno_error_l:
                    fw.write(json.dumps(item, ensure_ascii=False))
                    fw.write("\n")
            logger.info("the error img name has been save to the {}".format(anno_break_txt))
        else:
            print("there are no error in {}".format(self.list_path))

        len_img = len(os.listdir(self.img_dir))
        if len_anno != len_img:
            logger.warning("Unequal number of annotations and images!")


def img_classify_check(folder, output):
    check_data = ImgClassifyCheck(folder, output)
    check_data.is_img_break()
    check_data.is_anno_break()


if __name__ == '__main__':
    print("start")
