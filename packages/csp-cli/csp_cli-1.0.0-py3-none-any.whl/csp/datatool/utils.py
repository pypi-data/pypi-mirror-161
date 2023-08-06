#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/4/24 15:28
# @Author  : xgy
# @Site    : 
# @File    : utils.py
# @Software: PyCharm
# @python version: 3.7.4
"""
import json
import os

import chardet
import numpy as np
from loguru import logger

# import shutil
# import traceback

task_l = ["obj_det", "img_cls", "text_entity_extra", "text_entity_relation_extra", "text_cls"]


class JsonLoad:

    def __init__(self, json_path):
        self.file_path = json_path

    def encodetype(self):
        with open(self.file_path, 'rb') as f:
            try:
                data = f.read()
            except Exception as e:
                logger.error(e)
                return False
            f_charInfo = chardet.detect(data)
            # {'encoding': 'utf-8', 'confidence': 0.99, 'language': ''}
            if f_charInfo["encoding"] != "utf-8":
                logger.warning("Documents shall be encoded in UTF-8 format not {}".format(f_charInfo["encoding"]))
        return f_charInfo["encoding"]

    @property
    def data(self):
        # encode_type = self.encodetype()
        # if encode_type != "utf-8":
        #     logger.warning("Documents shall be encoded in UTF-8 format not {}".format(encode_type))
        try:
            with open(self.file_path, "r", encoding="utf-8") as fr:
                json_data = json.load(fr)
            return json_data
        except Exception as e:
            # print(traceback.print_exc())
            print("json file is error")
            return None


class Entity:

    def __init__(self, folder, output=None):
        self.folder = folder
        self.output = output if output else "./"
        self.label_categories_data = None
        self.labels_data = None
        self.sources_data = None
        self.connections_data = None
        self.connection_categories_data = None
        self.src_ids = []
        self.cate_ids = []
        self.cate_l = []
        self.conn_cate_ids = []

    def get_dataset(self):
        abs_path = os.path.abspath(self.folder)
        self.label_categories_path = os.path.join(abs_path, "labelCategories.json")
        self.labels_path = os.path.join(abs_path, "labels.json")
        self.sources_path = os.path.join(abs_path, "sources.json")
        self.connections_path = os.path.join(abs_path, "connections.json")
        self.connection_categories_path = os.path.join(abs_path, "connectionCategories.json")

        self.label_categories_data = JsonLoad(self.label_categories_path).data
        self.labels_data = JsonLoad(self.labels_path).data
        self.sources_data = JsonLoad(self.sources_path).data

        if os.path.exists(self.connections_path) and os.path.exists(self.connection_categories_path):
            self.connections_data = JsonLoad(self.connections_path).data
            self.connection_categories_data = JsonLoad(self.connection_categories_path).data

    def get_sources_ids(self):
        for item in self.sources_data:
            self.src_ids.append(item["id"])

    def get_cate_ids(self):
        for item in self.label_categories_data:
            self.cate_ids.append(item["id"])
            self.cate_l.append(item["text"])

    def get_conn_cate_ids(self):
        for item in self.connection_categories_data:
            self.conn_cate_ids.append(item["id"])

    def check_json(self, data):
        if data is None or not data:
            return False
        else:
            return True

    def clean_output(self):
        # shutil.rmtree(self.output)
        txt_l = ["connections_srcid_error.txt", "connections_categoryid_error.txt", "connectioncategory_error.txt",
                 "file_error.txt", "sources_error.txt", "labelcategory_error.txt", "labels_srcid_error.txt",
                 "labels_categoryid_error.txt"]
        for item in os.listdir(self.output):
            if item in txt_l:
                re_path = os.path.join(self.output, item)
                os.remove(re_path)

        os.makedirs(self.output, exist_ok=True)


class TxtFileCheck:

    def __init__(self, folder):
        self.folder = folder

    def txt_file_check(self, output=None):
        """
        判断 txt 文件是否打开异常、是否为 utf-8 编码
        :param output:
        :return:
        """
        txt_file_error_l = []
        abs_path = os.path.abspath(self.folder)
        for root, _, files in os.walk(abs_path):
            for file in files:
                txt_path = os.path.join(root, file)
                txt_ = JsonLoad(txt_path)
                file_encode = txt_.encodetype()
                if not file_encode:
                    logger.error("can not open {}".format(txt_path))
                    txt_file_error_l.append(txt_path)
                else:
                    if file_encode != "utf-8":
                        txt_file_error_l.append(txt_path)
                        logger.error("Documents shall be encoded in 'UTF-8' format, but {} is encoded in {}".format(txt_path, file_encode))
        if txt_file_error_l:
            save_path = os.path.join(output, "txt_file_error.txt") if output else "txt_file_error.txt"
            with open(save_path, "w", encoding="utf-8") as fw:
                for item in txt_file_error_l:
                    fw.write(item + "\n")
            logger.info("the result has been saved in {}".format(save_path))
        else:
            logger.info("the are no truble txt files")


class Filter:

    def __init__(self, size):
        self.size = size

    def choice_random(self, ratio: float, seed=2):
        assert 0 < ratio <= 1, 'ratio should between 0 and 1 (0<ratio<=1)'
        np.random.seed(seed)
        num = int(self.size * ratio)
        filter_index = np.random.choice(self.size, num, replace=False)
        return list(filter_index)


if __name__ == '__main__':
    print("start")
    test_json = "C:/Users/xgy/Desktop/CSPTools/0424/文本实体标注格式/labelCategories.json"
    test = JsonLoad(test_json)
    res = test.encodetype()
    test_data = test.data
