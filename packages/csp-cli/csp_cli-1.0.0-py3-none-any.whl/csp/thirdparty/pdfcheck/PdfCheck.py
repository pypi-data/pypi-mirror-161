#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/6/28 15:02
# @Author  : xgy
# @Site    : 
# @File    : PdfCheck.py
# @Software: PyCharm
# @python version: 3.7.4
"""

import csp.aip.PdfCheck
from csp.common.docker_server import DockerServer


class PdfCheck:
    # 镜像版本号，默认值
    def_version = "0.1"
    # 镜像容器端口，默认值
    def_port = "30003"
    # 镜像名称，默认值
    def_name = "pdf-check"

    def __init__(self, version=None, port=None, c_name=None, name=None, reload=True):
        if version:
            self.version = version
        else:
            self.version = self.def_version
        if port:
            self.port = port
        else:
            self.port = self.def_port
        if name:
            self.name = name
        else:
            self.name = self.def_name
        self.http_sdk = csp.aip.PdfCheck(ip="127.0.0.1", port=self.port)

        # self.port = port
        self.server = DockerServer(name=self.name, version=self.version, port=self.port, c_name=c_name, reload=reload)
        self.server.start()

    def check(self, file_path):
        """
        图谱创建
        """
        result = self.http_sdk.check(file_path)

        return result


if __name__ == '__main__':
    print("start")

