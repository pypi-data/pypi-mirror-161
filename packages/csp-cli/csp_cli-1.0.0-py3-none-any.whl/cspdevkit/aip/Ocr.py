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


from .common.http_client import HttpClient


class Ocr:
    # 镜像版本号，默认值
    def_version = "1.2"
    # 镜像容器端口，默认值
    def_port = "28888"
    # 镜像名称，默认值
    def_name = "yrocr-cpu"

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def ocr_text(self, img_path, drop_score='0.5'):
        """
        纯文本抽取，返回原始数据
        :param img_path: 图片路径
        :param drop_score: 可选参数
        :return:
        """
        http_client = HttpClient()
        url = "http://127.0.0.1:" + str(self.port) + "/ocr_text"

        files = {
            "file": open(img_path, 'rb'),
            "drop_score": (None, drop_score)
        }
        dt = http_client.post(url, arg_type="files", **files)
        result = dt["data"]
        return result

    def ocr_table(self, img_path, drop_score='0.1', erase_bound_padding='30'):
        """
        OCR表格识别(暂时支持90/190/270度旋转)
        :param img_path: 图片路径
        :param drop_score: 丢弃的置信度
        :param erase_bound_padding: 擦除的边界宽度
        :return:
        """
        http_client = HttpClient()
        url = "http://127.0.0.1:" + str(self.port) + "/ocr_table"

        files = {
            "file": open(img_path, 'rb'),
            "drop_score": (None, drop_score),
            "erase_bound_padding": (None, erase_bound_padding)
        }
        dt = http_client.post(url, arg_type="files", **files)
        result = dt["data"]
        return result

    def ocr_fixed_file(self, code, img_path, drop_score='0.5'):
        """
        识别固定格式的电子证照
        :param code: 格式编码。如：idcard/train_ticket/audit/safety_production_license
        :param img_path: 图片路径
        :param drop_score: 丢弃的分数
        :param use_show_name: 是否使用显示名称
        :return:
        """
        http_client = HttpClient()
        url = "http://127.0.0.1:" + str(self.port) + "/ocr_fixed_file"

        files = {
            "file": open(img_path, 'rb'),
            "format_file_code": (None, code),
            "drop_score": (None, drop_score),
            'use_show_name': (None, 'True')
        }
        dt = http_client.post(url, arg_type="files", **files)
        result = dt["data"]
        return result


if __name__ == '__main__':
    print("start")

    # ocr = Ocr(ip="127.0.0.1", port=28888)
    # test ocr_text
    # img_path = "C:/Users/xgy/Desktop/OCR_TABLE1.png"
    # print("start ocr text image:", img_path);
    # result = ocr.ocr_text(img_path)

    # test ocr_text
    # img_path = "/Users/liny/work/ocr/table.jpg";
    # print("start ocr table image:", img_path);
    # result = ocr.ocr_table(img_path);
    # print("ocr table result:",result);

    # test ocr_fixed_file
    # img_path = "/Users/liny/work/ocr/shenfz001.jpeg";
    # print("start ocr_fixed_file image:", img_path);
    # result = ocr.ocr_fixed_file("idcard", img_path);
    # print("ocr_fixed_file result:",result);


