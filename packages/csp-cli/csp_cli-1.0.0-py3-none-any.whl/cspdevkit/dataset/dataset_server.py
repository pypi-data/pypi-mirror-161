#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/5/18 9:53
# @Author  : xgy
# @Site    : 
# @File    : dataset_server.py
# @Software: PyCharm
# @python version: 3.7.4
"""
import json
import os
from datetime import datetime

# from csp.common.http_client import HttpClient
from csp.aip.common.http_client import HttpClient
from csp.common.config import Configure
from csp.common.utils import format


def data_list(name=None):
    interface_config = Configure().data
    http_client = HttpClient()

    url = interface_config["search"]["dataset"]
    params = {"name": name}
    res_dict = http_client.get(url, **params)

    # title_dict = {"名称": "name", "分类": "classify", "源数据": "rawDataNum", "训练数据": "trainDataNum", "验证数据": "evaDataNum",
    #               "创建时间": "createTime", "更新时间": "updateTime", "描述": "funDesc"}

    title_dict = {"名称": "name", "分类": "classify", "原始数据": "rawDataNum", "训练数据": "trainDataNum", "验证数据": "evaDataNum",
                  "创建时间": "createTime", "更新时间": "updateTime"}

    format(res_dict, title_dict)


def data_get(name=None, infer_type: str = None):
    interface_config = Configure().data
    http_client = HttpClient()

    url = interface_config["search"]["dataset"]
    params = {"name": name}
    res_dict = http_client.get(url, **params)

    if infer_type == "list" or infer_type == "search":
        title_dict = {"名称": "name", "分类": "classify", "原始数据": "rawDataNum", "标注数据": "trainDataNum",
                      "验证数据": "evaDataNum", "创建时间": "createTime", "更新时间": "updateTime"}

        format(res_dict, title_dict)
    if infer_type == "info":
        info_dict = {"名称": res_dict["data"][0]["name"],
                     "分类": res_dict["data"][0]["classify"],
                     "原始数据": res_dict["data"][0]["rawDataNum"],
                     "标注数据": res_dict["data"][0]["trainDataNum"],
                     "验证数据": res_dict["data"][0]["evaDataNum"],
                     "创建时间": res_dict["data"][0]["createTime"],
                     "更新时间": res_dict["data"][0]["updateTime"],
                     "描述": res_dict["data"][0]["funDesc"]}
        json_data = json.dumps(info_dict, ensure_ascii=False, indent=4)
        print(json_data)


def data_download(name, mode, size, output):
    interface_config = Configure().data
    http_client = HttpClient()

    # 按时间戳创建文件夹保存下载数据
    create_time = datetime.strftime(datetime.now(), "%Y%m%d%H%M%S%f")
    output = os.path.join(output, create_time)
    os.makedirs(output, exist_ok=True)

    url = interface_config["download"]["dataset"]
    params = {"name": name, "mode": mode, "size": size}
    res = http_client.download(url, output, **params)

    return res


if __name__ == '__main__':
    print("start")
    # name = "中标通知书"
    # output = "C:/Users/xgy/Desktop/CSPTools/infetr_test/"
