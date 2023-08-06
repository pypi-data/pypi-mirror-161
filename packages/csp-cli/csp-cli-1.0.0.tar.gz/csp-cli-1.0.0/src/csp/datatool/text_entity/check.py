#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/4/24 16:14
# @Author  : xgy
# @Site    : 
# @File    : check.py
# @Software: PyCharm
# @python version: 3.7.4
"""
import json
import os

from loguru import logger

from csp.datatool.utils import Entity


class EntityCheck(Entity):

    def __init__(self, folder, output=None):
        super(EntityCheck, self).__init__(folder, output)

    def check_sources(self):
        """
        公共检查，sources.json 字段值为空
        :return:
        """
        sources_error_l = []
        # 检查字段全为空为空

        sources_flg = True

        for index, item in enumerate(self.sources_data):
            if item["id"]:
                if not item["title"] or not item["content"]:
                    error_item = {"message": "the title or content is empty", "data": {"id": item["id"]}}
                    sources_error_l.append(error_item)
            else:
                logger.error("some sources information is empty")
                error_item = {"message": "the title or content is empty", "data": item}
                sources_error_l.append(error_item)
                # sources_flg = False

        if sources_error_l:
            save_path = os.path.join(self.output, "sources_error.txt") if self.output else "sources_error.txt"
            with open(save_path, "w", encoding="utf-8") as fw:
                for item in sources_error_l:
                    fw.write(json.dumps(item, ensure_ascii=False))
                    fw.write("\n")
                logger.error("the sources.json error information saved in {}".format(save_path))
            sources_flg = False
        else:
            if sources_flg:
                logger.info("the is no trouble in sources.json")

        return sources_flg

    def check_labelcategory(self):
        """
        公共检查，labelcategory.json 字段值为空
        :return:
        """
        labelcategorys_flg = True

        labelcategory_error_l = []
        # 检查字段全为空为空

        for item in self.label_categories_data:
            if not item["id"] and not item["text"]:
                logger.error("some label category information are empty")
                error_item = {"message": "the text is empty", "data": {"id": item["id"]}}
                labelcategory_error_l.append(error_item)
                # labelcategorys_flg = False
            if item["id"] and not item["text"]:
                error_item = {"message": "the text is empty", "data": {"id": item["id"]}}
                labelcategory_error_l.append(error_item)
            if not item["id"] and item["text"]:
                error_item = {"message": "the id is empty", "data": {"id": item["id"]}}
                labelcategory_error_l.append(error_item)

        if labelcategory_error_l:
            save_path = os.path.join(self.output, "labelcategory_error.txt") if self.output else "labelcategory_error.txt"
            with open(save_path, "w", encoding="utf-8") as fw:
                for item in labelcategory_error_l:
                    fw.write(json.dumps(item, ensure_ascii=False))
                    fw.write("\n")
                logger.error("the labelcategories.json error information saved in  {}".format(save_path))
            labelcategorys_flg = False
        else:
            if labelcategorys_flg:
                logger.info("the is no trouble in labelcategories.json")
        return labelcategorys_flg

    def check_labels(self):
        srcId_error_l = []
        categoryId_error_l = []
        self.get_sources_ids()
        self.get_cate_ids()
        for index, item in enumerate(self.labels_data):
            if item["srcId"] not in self.src_ids:
                error_item = {"message": "srcId not in sources.json", "data": item}
                srcId_error_l.append(error_item)
            if item["categoryId"] not in self.cate_ids:
                error_item = {"message": "categoryId not in labelCategories.json", "data": item}
                categoryId_error_l.append(error_item)
            # 兼容文本分类任务的labels.json格式
            category_name = item.get("value", 0)
            if not category_name and category_name != 0:
                error_item = {"message": "category value is empty", "data": item}
                categoryId_error_l.append(error_item)
            if category_name and (category_name not in self.cate_l):
                error_item = {"message": "category value not in {}".format(self.label_categories_path), "data": item}
                categoryId_error_l.append(error_item)

        if srcId_error_l:
            save_path = os.path.join(self.output, "labels_srcid_error.txt") if self.output else "labels_srcid_error.txt"
            with open(save_path, "w", encoding="utf-8") as fw:
                for item in srcId_error_l:
                    fw.write(json.dumps(item, ensure_ascii=False))
                    fw.write("\n")
                logger.error("the srcId error information has been saved in {}".format(save_path))
        if categoryId_error_l:
            save_path = os.path.join(self.output, "labels_categoryid_error.txt") if self.output else "labels_categoryid_error.txt"
            with open(save_path, "w", encoding="utf-8") as fw:
                for item in categoryId_error_l:
                    fw.write(json.dumps(item, ensure_ascii=False))
                    fw.write("\n")
                logger.error("the  categoryId error information has been saved in {}".format(save_path))
        if not srcId_error_l and not categoryId_error_l:
            logger.info("the is no trouble in labels.json")

    def check_json(self, data=None):
        is_json_sources = super().check_json(self.sources_data)
        is_json_labels = super().check_json(self.labels_data)
        is_json_labelcategories = super().check_json(self.label_categories_data)

        save_path = os.path.join(self.output, "file_error.txt") if self.output else "file_error`.txt`"
        if not is_json_sources:
            with open(save_path, "a+", encoding="utf-8") as fw:
                error_item = {"file_name": self.sources_path, "message": "the file can not be load or the file is empty"}
                fw.write(json.dumps(error_item, ensure_ascii=False))
                fw.write("\n")

        if not is_json_labels:
            with open(save_path, "a+", encoding="utf-8") as fw:
                error_item = {"file_name": self.labels_path, "message": "the file can not be load or the file is empty"}
                fw.write(json.dumps(error_item, ensure_ascii=False))
                fw.write("\n")

        if not is_json_labelcategories:
            with open(save_path, "a+", encoding="utf-8") as fw:
                error_item = {"file_name": self.label_categories_path, "message": "the file can not be load or the file is empty"}
                fw.write(json.dumps(error_item, ensure_ascii=False))
                fw.write("\n")

        if not is_json_sources or not is_json_labels or not is_json_labelcategories:
            logger.error("json file error information saved in {}".format(save_path))
            return False
        else:
            return True


def entity_check(folder, output=None):
    check_entity = EntityCheck(folder, output=output)
    check_entity.clean_output()
    check_entity.get_dataset()

    # 第一步判断json文件是否能打开
    flag_json = check_entity.check_json()

    if flag_json:
        flag_sources = check_entity.check_sources()
        flag_labelcategory = check_entity.check_labelcategory()

        if flag_sources and flag_labelcategory:
            check_entity.check_labels()
        else:
            logger.warning("there are some error exist in {} or {}. The file labels.json will not be checked".format(check_entity.sources_path, check_entity.label_categories_path))


if __name__ == '__main__':
    print("start")
