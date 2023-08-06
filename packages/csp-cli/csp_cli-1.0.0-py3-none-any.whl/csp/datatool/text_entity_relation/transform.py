#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/6/23 9:24
# @Author  : xgy
# @Site    : 
# @File    : transform.py
# @Software: PyCharm
# @python version: 3.7.4
"""

import json
import os
import sys
import click

# from loguru import logger
from csp.datatool.text_entity_relation.spo_utils.standard2doccano import standard2doccno
from csp.datatool.text_entity_relation.spo_utils.uiespo2standard import uiespo2standard
from csp.datatool.text_entity_relation.spo_utils.standard2kg import ud2table


class St2Doccno:

    def __init__(self, folder, output):
        self.standard_path = folder
        self.output = output

        os.makedirs(self.output, exist_ok=True)

        self.label_category_path = os.path.join(self.standard_path, "labelCategories.json")
        self.source_path = os.path.join(self.standard_path, "sources.json")
        self.label_path = os.path.join(self.standard_path, "labels.json")
        self.connection_path = os.path.join(self.standard_path, "connections.json")
        self.connection_category_path = os.path.join(self.standard_path, "connectionCategories.json")

        self.data_connection_category = []
        self.data_label_category = []
        self.data_source = []
        self.data_label = []
        self.data_connection = []
        self.dict_label_category = {}
        self.dict_connection_category = {}

        self.id2labelCategory = {}
        self.id2connectionCategorie = {}

    def transform(self):

        self.data_proc()
        series_doccano = self.get_doccano()

        file_name = "standard2doccano_ext.json"

        output_item = os.path.join(self.output, file_name)
        with open(output_item, "w", encoding="utf-8") as f:
            for item in series_doccano:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

        relations = self.gen_relation()
        file_name = "relations.json"
        output_item = os.path.join(self.standard_path, file_name)
        with open(output_item, "w", encoding="utf-8") as f:
            f.write(json.dumps(relations, ensure_ascii=False, indent=4))

    def check_file(self):
        result_json = {}
        if not os.path.isfile(self.label_category_path) or not os.path.exists(self.label_category_path):
            result_json["error_code"] = 1001
            result_json["error_msg"] = ("未找到实体类别数据label_category文件 %s" % self.label_category_path)
            click.echo(json.dumps(result_json, ensure_ascii=False))
            sys.exit(1)

        if self.connection_category_path:
            if not os.path.isfile(self.connection_category_path) or not os.path.exists(self.connection_category_path):
                result_json["error_code"] = 1002
                result_json["error_msg"] = ("未找到实体类别数据connection_category文件 %s" % self.connection_category_path)
                click.echo(json.dumps(result_json, ensure_ascii=False))
                sys.exit(1)

        if not os.path.isfile(self.source_path) or not os.path.exists(self.source_path):
            result_json["error_code"] = 1003
            result_json["error_msg"] = ("未找到原始数据source文件 %s" % self.source_path)
            click.echo(json.dumps(result_json, ensure_ascii=False))
            sys.exit(1)

        if not os.path.isfile(self.label_path) or not os.path.exists(self.label_path):
            result_json["error_code"] = 1004
            result_json["error_msg"] = ("未找到实体标注数据label文件 %s" % self.label_path)
            click.echo(json.dumps(result_json, ensure_ascii=False))
            sys.exit(1)

        if self.connection_path:
            if not os.path.isfile(self.connection_path) or not os.path.exists(self.connection_path):
                result_json["error_code"] = 1005
                result_json["error_msg"] = ("未找到关系标注数据connection文件 %s" % self.connection_path)
                click.echo(json.dumps(result_json, ensure_ascii=False))
                sys.exit(1)

        if not os.path.isdir(self.output):
            result_json["error_code"] = 1004
            result_json["error_msg"] = ("output应为文件夹路径 %s" % self.output)
            click.echo(json.dumps(result_json, ensure_ascii=False))
            os.remove(self.output)
            sys.exit(1)

    def data_proc(self):
        """
        数据预处理
        对原始数据读取和转换
        并赋值全局变量
        """
        # global data_label_category, data_connection_category, data_source, data_label, data_connection, id2labelCategory, id2connectionCategorie
        self.data_label_category = self.read_json(self.label_category_path)
        if self.connection_category_path:
            self.data_connection_category = self.read_json(self.connection_category_path)
        self.data_source = self.read_json(self.source_path)
        self.data_label = self.read_json(self.label_path)
        if self.connection_path:
            self.data_connection = self.read_json(self.connection_path)

        self.id2labelCategory = {str(row['id']): row['text'] for row in self.data_label_category}
        self.id2connectionCategorie = {str(row['id']): row['text'] for row in self.data_connection_category}

    @staticmethod
    def read_json(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    def get_doccano(self):
        """
        主程序
        数据组装
        """
        series = []
        for source in self.data_source:
            result = {}

            text_id = str(source["id"])
            # result["id"] = int(source["id"])
            # id 可能不为数字 ‘209365750100ce2e62ddc6795c8f3215’
            result["id"] = source["id"]
            result["text"] = source["content"].replace('\r\n', '**')

            result["entities"] = self.get_labels(text_id)
            result["relations"] = self.get_connections(text_id)

            series.append(result)
        return series

    def get_labels(self, text_id):
        """
        组装实体数据
        """
        labels = []
        for label in self.data_label:
            result_label = {"id": int(label["id"])}
            # result_label = {"id": label["id"]}
            srcId = str(label["srcId"])
            if text_id == srcId:
                label_category = self.id2labelCategory[str(label["categoryId"])]
                result_label["label"] = label_category
                # result_label["name"] = label["name"]
                result_label["start_offset"] = int(label["startIndex"])
                result_label["end_offset"] = int(label["endIndex"])
                labels.append(result_label)
        return labels

    def get_connections(self, text_id):
        """
        组装关系数据
        """
        if self.data_connection:
            connections = []
            for connection in self.data_connection:
                result_connection = {"id": int(connection["id"])}
                # result_connection = {"id": connection["id"]}
                srcId = str(connection["srcId"])
                if text_id == srcId:
                    connection_category = self.id2connectionCategorie[str(connection["categoryId"])]
                    result_connection["type"] = connection_category
                    result_connection["from_id"] = int(connection["fromId"])
                    result_connection["to_id"] = int(connection["toId"])
                    connections.append(result_connection)
        else:
            connections = []

        return connections

    def gen_relation(self):
        '''
        生成 实体-关系-实体 集
        方便其他格式转回 公司标注数据格式
        '''
        # 转数据
        relations = []
        str_relations = []
        labels2id = {row['srcId'] + str(row['id']): row for row in self.data_label}
        labelCategories_dict = {str(row['id']): row['text'] for row in self.data_label_category}
        connectionCategories_dict = {str(row['id']): row['text'] for row in self.data_connection_category}
        for row in self.data_connection:
            srcId = row['srcId']
            categoryId = row['categoryId']
            fromId = srcId + str(row['fromId'])
            toId = srcId + str(row['toId'])
            # 获取实体类型ID
            from_categoryId = labels2id[fromId]['categoryId']
            to_categoryId = labels2id[toId]['categoryId']
            str_relation = str(categoryId) + str(to_categoryId) + str(from_categoryId)
            if str_relation in str_relations:
                continue
            relations.append({
                "categoryId": categoryId,
                "toId": to_categoryId,
                "fromId": from_categoryId
            })
            str_relations.append(str_relation)

            # 获取关系类型
            category = connectionCategories_dict[str(categoryId)]
            # 获取实体类型
            from_category = labelCategories_dict[str(from_categoryId)]
            to_category = labelCategories_dict[str(to_categoryId)]
            print({
                "fromId": from_category,
                "categoryId": category,
                "toId": to_category
            })
        return relations

# class Uie2standard:
#     """
#     将uie预测结果转为标准格式
#     uie的训练数据为标准格式数据
#     转换过程需用到训练数据的部分文件
#     """
#
#     def __init__(self, uie_file, ori_folder, output):
#         self.spo_file = uie_file
#         self.ori_folder = ori_folder
#         self.output = output
#         self.label_categories_path = os.path.join(ori_folder, "labelCategories.json")
#         self.connection_categories_path = os.path.join(ori_folder, "connectionCategories.json")
#         self.relations_path = os.path.join(ori_folder, "relations.json")
#
#         os.makedirs(output, exist_ok=True)
#
#     def transform(self):
#
#         if not self.check_input_file():
#             sys.exit(1)
#
#         data_proc(label_categories_path, relations_path, connection_categories_path)
#
#         data_spo = read_txts(spo_file)
#
#         series_source = get_source(data_spo)
#         series_label, series_connection = get_label_connection(data_spo)
#
#         file_label_category = "labelCategories" + ".json"
#         file_connection_category = "connectionCategories" + ".json"
#         file_source = "sources" + ".json"
#         file_label = "labels" + ".json"
#         file_connection = "connections" + ".json"
#         file_relation = "relations" + ".json"
#
#         copy_file(label_categories_path, output, file_label_category)
#         copy_file(connection_categories_path, output, file_connection_category)
#         copy_file(relations_path, output, file_relation)
#
#         write_file(series_source, output, file_source)
#         write_file(series_label, output, file_label)
#         if series_connection:
#             write_file(series_connection, output, file_connection)
#
#     def check_input_file(self):
#         # result_json = {}
#         # if not os.path.exists(self.spo_file):
#         #     result_json["error_code"] = 1001
#         #     result_json["error_msg"] = ("未找到待转换的标注数据工具数据文件 %s" % self.spo_file)
#         #     print(json.dumps(result_json, ensure_ascii=False))
#         #     sys.exit(1)
#
#         file_path_arr = [self.spo_file, self.label_categories_path, self.connection_categories_path, self.relations_path]
#         for file_path in file_path_arr:
#             if not os.path.exists(file_path) or not os.path.isfile(file_path):
#                 self.print_error_msg(("指定的文件路径不存在: %s" % file_path), 1001)
#                 return False
#         return True
#
#     @staticmethod
#     def print_error_msg(msg, code):
#         result_json = {}
#         result_json['error_msg'] = msg
#         result_json['error_code'] = code
#         print(json.dumps(result_json, ensure_ascii=False))


def spo_transform(folder, form, output, uie_file=None):
    if form.lower() == "standard2doccano":
        standard2doccno(folder, output)
        # spotransform = St2Doccno(folder, output)
        # spotransform.transform()
    elif form.lower() == "uie2standard":
        uiespo2standard(uie_file, folder, output)
    elif form.lower() == "standard2kg":
        ud2table(folder, output)
    else:
        raise KeyError("the from should be standard2doccano/uie2standard/standard2kg in task text_entity_relation_extra")


if __name__ == '__main__':
    print("start")

    # test_dir = "C:/Users/xgy/Desktop/CSPTools/0424/文本实体关系三元组标注格式/transform/ori"
    # test_form = "standard"
    # output_dir = "C:/Users/xgy/Desktop/CSPTools/0424/文本实体关系三元组标注格式/transform/st2doccano"

    test_dir = "C:/Users/xgy/Desktop/CSPTools/0424/文本实体关系三元组标注格式/transform/ud2table"
    test_form = "standard2table"
    output_dir = "C:/Users/xgy/Desktop/CSPTools/0424/文本实体关系三元组标注格式/transform/output_ud2table"

    spo_transform(test_dir, test_form, output_dir)

    # test_dir = "C:/Users/xgy/Desktop/CSPTools/0424/文本实体关系三元组标注格式/transform/uie/standard"
    # uie = "C:/Users/xgy/Desktop/CSPTools/0424/文本实体关系三元组标注格式/transform/uie/uiespo.json"
    # test_form = "uie"
    # output_dir = "C:/Users/xgy/Desktop/CSPTools/0424/文本实体关系三元组标注格式/transform/output_uie"

    # spo_transform(test_dir, test_form, output_dir, uie_file=uie)


