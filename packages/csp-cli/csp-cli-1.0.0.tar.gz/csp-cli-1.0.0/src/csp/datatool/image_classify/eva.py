#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/6/30 10:13
# @Author  : xgy
# @Site    : 
# @File    : eva.py
# @Software: PyCharm
# @python version: 3.7.4
"""

import os
from loguru import logger
import pandas as pd
# from sklearn.metrics import classification_report

from csp.common.utils import RunSys, print_error_msg


class ImgClassifyEva:

    def __init__(self, submit_file, gold_folder, output=None):
        self.submit_path = submit_file
        self.gold_folder = gold_folder
        self.gold_path = os.path.join(self.gold_folder, "test_list.txt")
        self.labels_path = os.path.join(self.gold_folder, "labels.txt")
        self.output = output
        self.path_prefix = None

    def check_file(self):
        file_path_arr = [self.submit_path, self.gold_path, self.labels_path]
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

        labels_dict, labels_l = self.get_labels_dict()

        labels_n = []
        y_true = []
        y_pred = []
        for k, v in data_true.items():
            y_true.append(str(v))
            y_pred.append(data_pred.get(k))
            if labels_dict[str(v)] not in labels_n:
                labels_n.append(labels_dict[str(v)])

        target_names = []
        for i in range(len(labels_dict)):
            item = labels_dict[str(i)]
            if item in labels_n:
                target_names.append(item)

        # t = classification_report(y_true, y_pred, target_names=target_names)
        t = classification_report(y_true, y_pred, target_names=target_names, output_dict=True)
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

    def get_data_dict(self, txt_path):
        data_dict = {}
        with open(txt_path, "r", encoding="utf-8") as fr:
            data_l = fr.readlines()

            for item in data_l:
                item = item.replace("\n", "")

                # 兼容文件路径分隔符
                if "/" in item and "\\\\" not in item:
                    item_split = item.split(" ")[0].split("/")
                    file_name = item_split[-1]
                elif "/" not in item and "\\\\" in item:
                    item_split = item.split(" ")[0].split("\\\\")
                    file_name = item_split[-1]
                elif "/" in item and "\\\\" in item:
                    item_split = item.split(" ")[0].split("\\\\")
                    if "/" in item_split[-1]:
                        item_split = item_split[-1].split("/")
                        file_name = item_split[-1]
                    else:
                        file_name = item_split[-1]
                else:
                    file_name = item.split(" ")[0].lstrip(".")
                data_dict[file_name] = item.split(" ")[1]

                if not self.path_prefix:
                    path_prefix = item.split(" ")[0].replace(file_name, "")
                    self.path_prefix = path_prefix

        return data_dict

    def get_labels_dict(self):
        labels_dict = {}
        labels = []
        labels_path = os.path.join(self.gold_folder, "labels.txt")
        with open(labels_path, "r", encoding="utf-8") as fr:
            labels_l = fr.readlines()
            for index, label in enumerate(labels_l):
                labels_dict[str(index)] = label.replace("\n", "")
                labels.append(label.replace("\n", ""))
        return labels_dict, labels


def img_classify_eva(submit_file, gold_folder, output=None):
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

    data_eva = ImgClassifyEva(submit_file, gold_folder, output)
    data_eva.eva()


if __name__ == '__main__':
    print("start")
