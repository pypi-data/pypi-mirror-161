#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/7/13 10:46
# @Author  : xgy
# @Site    : 
# @File    : docker_base.py
# @Software: PyCharm
# @python version: 3.7.4
"""
# import csp
from csp.aip.common.http_client import HttpClient
from csp.common.docker_server import DockerServer


# class BaseAipDocker:
#
#     def __init__(self, ip, port, name=None, version=None, c_port=None, c_name=None, c_param=None, reload=True):
#         self.name = name
#         self.version = version
#         self.ip = ip
#         self.port = port
#         self.c_port = c_port
#         self.c_name = c_name
#         self.c_param = c_param
#         self.reload = reload


class AipKg:

    def __init__(self, ip, port):
        # super(AipKg, self).__init__(ip, port)
        self.ip = ip
        self.port = port

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


class ServerKg(AipKg):

    def __init__(self, ip="127.0.0.1", port='30001', name='kg', version='1.1', c_port='5000', c_name=None, c_param=None, reload=True):
        super(ServerKg, self).__init__(ip, port)
        # super(AipKg, self).__init__(ip, port, name, version, c_port, c_name, c_param, reload)

        self.server = DockerServer(name, version, port, c_port, c_name, c_param, reload)
        self.server.start()


if __name__ == '__main__':
    print("start")
