#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/7/1 10:44
# @Author  : xgy
# @Site    : 
# @File    : eva.py
# @Software: PyCharm
# @python version: 3.7.4
"""
import json
import os
from loguru import logger
import pandas as pd
# from sklearn.metrics import classification_report

from csp.common.utils import RunSys, print_error_msg


class TextClassifyEva:

    def __init__(self, submit_file, gold_folder, output=None):
        self.submit_path = submit_file
        self.gold_folder = gold_folder
        self.gold_path = os.path.join(self.gold_folder, "labels.json")
        self.labelcategory_path = os.path.join(self.gold_folder, "labelCategories.json")
        self.output = output

    def check_file(self):
        file_path_arr = [self.submit_path, self.gold_path, self.labelcategory_path]
        for file_path in file_path_arr:
            if not os.path.exists(file_path) or not os.path.isfile(file_path):
                print_error_msg(("指定的文件路径不存在: %s" % file_path), 1001)
                return False
        return True

    def eva(self):

        self.check_file()
        from sklearn.metrics import classification_report

        logger.info("the gold file is {}".format(self.gold_path))
        logger.info("the predict file is {}".format(self.submit_path))

        data_true = self.get_data_dict(self.gold_path)
        data_pred = self.get_data_dict(self.submit_path)

        # labels_dict, labels_l = self.get_labels_dict()

        y_true = []
        y_pred = []
        for k, v in data_true.items():
            y_true.append(str(v))
            y_pred.append(data_pred.get(k))

        t = classification_report(y_true, y_pred, output_dict=True)
        series = []
        for k, v in t.items():
            if k == 'accuracy':
                series.append(
                    {"category": k,
                     'precision': '',
                     'recall': '',
                     'f1-score': v})
            else:
                series.append(
                    {"category": k,
                     'precision': v["precision"],
                     'recall': v["recall"],
                     'f1-score': v["f1-score"]})
        df_result = pd.DataFrame(data=series)
        df_result = df_result[['category', 'precision', 'recall', 'f1-score']]
        print(df_result)

        os.makedirs(self.output, exist_ok=True)
        output_path = os.path.join(self.output, "eva_result.csv")
        df_result.to_csv(output_path, index=False, sep=",", encoding="utf-8")

    def get_data_dict(self, json_file):
        data_dict = {}
        with open(json_file, "r", encoding="utf-8") as fr:
            data_l = json.load(fr)

            for item in data_l:
                data_dict[item["srcId"]] = item["value"]

        return data_dict

    # def get_labels_dict(self):
    #     labels_dict = {}
    #     labels = []
    #     with open(self.labelcategory_path, "r", encoding="utf-8") as fr:
    #         labels_l = json.load(fr)
    #         for item in labels_l:
    #             labels_dict[item["id"]] = item["text"]
    #             labels.append(item["text"])
    #     return labels_dict, labels


def text_classify_eva(submit_file, gold_folder, output=None):
    """
    需注意 submit_file, gold_file 的格式
    """
    # pip install sklearn
    try:
        from sklearn.metrics import classification_report
    except ImportError:
        logger.error("there is no scikit-learn try to install it, pip install scikit-learn")
        install_cmd = "pip install scikit-learn"

        RunSys(command=install_cmd).run_cli()

    data_eva = TextClassifyEva(submit_file, gold_folder, output)
    data_eva.eva()


if __name__ == '__main__':
    print("start")

