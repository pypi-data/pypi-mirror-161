#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/6/28 15:04
# @Author  : xgy
# @Site    : 
# @File    : PdfCheck.py
# @Software: PyCharm
# @python version: 3.7.4
"""

from .common.http_client import HttpClient


class PdfCheck:
    # 镜像版本号，默认值
    def_version = "0.1"
    # 镜像容器端口，默认值
    def_port = "30002"
    # 镜像名称，默认值
    def_name = "pdf-check"

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def check(self, file_path):
        """
        图谱构建
        """
        http_client = HttpClient()
        # url = "http://127.0.0.1:" + str(self.port) + "/kgExtension/createKg"
        url = "http://" + self.ip + ":" + str(self.port) + "/web/aip/pdf_check_txt"

        files = {
            "file": open(file_path, 'rb')
        }

        dt = http_client.post(url, arg_type="files", **files)

        res_msg = dt["data"]

        return res_msg


if __name__ == '__main__':
    print("start")


