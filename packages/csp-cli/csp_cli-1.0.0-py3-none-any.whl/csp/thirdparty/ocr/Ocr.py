#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/6/7 15:37
# @Author  : liny
# @Site    :
# @File    : Ocr.py
# @Software: IDEA
# @python version: 3.7.4
"""
import csp.aip.Ocr
from csp.common.docker_server import DockerServer
# from csp.common.http_client import HttpClient
# from csp.aip.common.http_client import HttpClient


class Ocr:
    # 镜像版本号，默认值
    def_version = "1.2"
    # 镜像容器端口，默认值
    def_port = "28888"
    # 镜像名称，默认值
    def_name = "yrocr-cpu"

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
        self.http_sdk = csp.aip.Ocr(ip="127.0.0.1", port=self.port)

        # self.port = port
        self.server = DockerServer(name=self.name, version=self.version, port=self.port, c_name=c_name, reload=reload)
        self.server.start()

    def ocr_text(self, img_path, drop_score='0.5'):
        """
        纯文本抽取，返回原始数据
        :param img_path: 图片路径
        :param drop_score: 可选参数
        :return:
        """
        result = self.http_sdk.ocr_text(img_path, drop_score)

        return result

    def ocr_table(self, img_path, drop_score='0.1', erase_bound_padding='30'):
        """
        OCR表格识别(暂时支持90/190/270度旋转)
        :param img_path: 图片路径
        :param drop_score: 丢弃的置信度
        :param erase_bound_padding: 擦除的边界宽度
        :return:
        """

        result = self.http_sdk.ocr_table(img_path, drop_score, erase_bound_padding)

        return result

    def ocr_fixed_file(self, code, img_path, drop_score='0.5'):
        """
        识别固定格式的电子证照
        :param format_file_code: 格式编码。如：idcard/train_ticket/audit/safety_production_license
        :param img_path: 图片路径
        :param drop_score: 丢弃的分数
        :param use_show_name: 是否使用显示名称
        :return:
        """
        result = self.http_sdk.ocr_fixed_file(code, img_path, drop_score)

        return result


if __name__ == '__main__':
    print("start")
    ocr = Ocr()
    # test ocr_text
    # img_path = "C:/Users/xgy/Desktop/OCR_TABLE1.png"
    # print("start ocr text image:", img_path);
    # result = ocr.ocr_text(img_path)
    # print("ocr text result:", result);

    # test ocr_table
    img_path = "C:/Users/xgy/Desktop/OCR_TABLE1.png"
    print("start ocr table image:", img_path)
    result = ocr.ocr_table(img_path)
    print("ocr table result:", result)

    # test ocr_fixed_file
    # img_path = "/Users/liny/work/ocr/shenfz001.jpeg";
    # print("start ocr_fixed_file image:", img_path);
    # result = ocr.ocr_fixed_file("idcard", img_path);
    # print("ocr_fixed_file result:",result);


