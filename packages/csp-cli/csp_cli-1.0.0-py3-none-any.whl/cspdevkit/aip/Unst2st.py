#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/5/19 17:55
# @Author  : xgy
# @Site    : 
# @File    : Unst2st.py
# @Software: PyCharm
# @python version: 3.7.4
"""
import base64
import os

from .common.http_client import HttpClient
# from http_client import HttpClient
# from .http_client import HttpClient


class Unst2st:
    # 镜像版本号，默认值
    def_version = "0.3"
    # 镜像容器端口，默认值
    def_port = "9889"
    # 镜像名称，默认值
    def_name = "unst2st"

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def extract_text(self, file, output=None):
        http_client = HttpClient()
        url = "http://" + self.ip + ":" + str(self.port) + "/web/aip/file2txt"
        files = {"file": open(file, 'rb')}

        dt = http_client.post(url, arg_type="files", **files)
        result = dt["data"]

        if output:
            txt_name = os.path.splitext(os.path.basename(file))[0] + ".txt"
            save_path = os.path.join(output, txt_name)
            with open(save_path, "w", encoding="utf-8") as fw:
                fw.write(result)

        return result

    def remove_watermark(self, file, output):
        http_client = HttpClient()
        # url = "http://127.0.0.1:" + str(self.port) + "/web/aip/remove_watermark_pdf_txt"
        url = "http://" + self.ip + ":" + str(self.port) + "/web/aip/remove_watermark_pdf_txt"
        files = {"file": open(file, 'rb')}

        # dt = http_client.convert(url, method="post", arg_type="files", **files)
        dt = http_client.post(url, arg_type="files", **files)
        result = dt["data"]

        with open(output, 'wb') as f:
            f.write(base64.b64decode(result))
        print("the output has been saved in {}".format(output))

        return result

    def extract_img_txt(self, file, output=None):
        """
        图片内容提取
        :param file: 文件路径
        :param output: 结果输出
        :return:
        """
        http_client = HttpClient()
        url = "http://" + self.ip + ":" + str(self.port) + "/web/aip/ocr"
        files = {"file": open(file, 'rb')}

        dt = http_client.post(url, arg_type="files", **files)
        result = dt["data"]

        if output:
            txt_name = os.path.splitext(os.path.basename(file))[0] + ".txt"
            save_path = os.path.join(output, txt_name)
            with open(save_path, "w", encoding="utf-8") as fw:
                fw.write(result)

        return result

    def extract_table(self, file, output=None):
        """
        表格提取
        :param file: 文件路径
        :param output: 结果输出
        :return:
        """
        http_client = HttpClient()
        url = "http://" + self.ip + ":" + str(self.port) + "/web/aip/table"
        files = {"file": open(file, 'rb')}

        # dt = http_client.convert(url, method="post", arg_type="files", **files)
        dt = http_client.post(url, arg_type="files", **files)
        result = dt["data"]

        if output:
            txt_name = os.path.splitext(os.path.basename(file))[0] + ".txt"
            save_path = os.path.join(output, txt_name)
            with open(save_path, "w", encoding="utf-8") as fw:
                fw.write(result)

        return result

    def extract_structure(self, file, output=None):
        """
        篇章段落抽取
        :param file: 文件路径
        :param output: 结果输出
        :return:
        """
        http_client = HttpClient()
        url = "http://" + self.ip + ":" + str(self.port) + "/web/aip/structure"
        files = {"file": open(file, 'rb')}

        dt = http_client.post(url, arg_type="files", **files)
        result = dt["data"]

        if output:
            txt_name = os.path.splitext(os.path.basename(file))[0] + ".txt"
            save_path = os.path.join(output, txt_name)
            with open(save_path, "w", encoding="utf-8") as fw:
                fw.write(result)

        return result


if __name__ == '__main__':
    print("start")

    # name = "unst2st"
    # ip = "127.0.0.1"
    # port = 9889
    # unst2st = Unst2st(ip, port)

    # file_path = "C://Users/xgy/desktop/P020190630537259577129.pdf"
    # #file_path = "C://Users/xgy/desktop/P020190630537259577129.pdf"
    # txt_1 = unst2st.extract_text(file_path)

    # test_pdf = "C:/Users/xgy/Desktop/doc_o.pdf"
    # out_file = "./out.pdf"
    # data_base64 = unst2st.remove_watermark(test_pdf, out_file)

    # file_path = "/Users/liny/work/ocr/命令行工具建设.docx";
    # txt_1 = unst2st.extract_text(file_path)
    # print("result:", txt_1);

    # file_path = "/Users/liny/work/ocr/tableTest.xlsx";
    # file_path = "/Users/liny/work/ocr/table.docx";
    # txt_1 = unst2st.extract_table(file_path)
    # print("result:", txt_1);

    # file_path = "/Users/liny/work/ocr/命令行工具建设.docx";
    # txt_1 = unst2st.extract_structure(file_path)
    # print("result:", txt_1);

    # file_path = "/Users/liny/work/ocr/text.png";
    # txt_1 = unst2st.extract_img_txt(file_path)
    # print("result:", txt_1);

