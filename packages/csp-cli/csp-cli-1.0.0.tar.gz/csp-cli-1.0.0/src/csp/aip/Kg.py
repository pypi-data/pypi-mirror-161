#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/6/28 15:04
# @Author  : xgy
# @Site    : 
# @File    : Kg.py
# @Software: PyCharm
# @python version: 3.7.4
"""

from .common.http_client import HttpClient


class Kg:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def create(self, class_file, code, link_file, name, node_file):
        """
        图谱构建
        """
        http_client = HttpClient()
        url = "http://" + self.ip + ":" + str(self.port) + "/kgExtension/createKg"

        files = {
            "classFile": open(class_file, 'rb'),
            "linkFile": open(link_file, 'rb'),
            "nodeFile": open(node_file, 'rb')
        }
        data = {"name": name, "code": code}
        params = {"files": files, "data": data}
        dt = http_client.post(url, arg_type="data/files", **params)

        kg_url = dt["data"]
        print("the kg has been create successful at {}".format("http://" + self.ip + ":" + str(self.port) + kg_url))
        return kg_url

    def list(self):
        """
        图谱列表查询
        """
        http_client = HttpClient()
        url = "http://" + self.ip + ":" + str(self.port) + "/kgInfo/lists"

        dt = http_client.get(url)

        result = dt["data"]
        result["url"] = "http://" + self.ip + ":" + str(self.port) + result["url"]

        return result

    def delete(self, code):
        """
        图谱删除
        """
        http_client = HttpClient()
        url = "http://" + self.ip + ":" + str(self.port) + "/kgInfo/delete"

        data = {"code": code}

        dt = http_client.post(url, arg_type="data", **data)

        result = dt
        print(result['msg'])

        return result


if __name__ == '__main__':
    print("start")


