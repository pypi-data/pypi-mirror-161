#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/7/01 15:31
# @Author  : liny
# @Site    : 
# @File    : Translate.py
# @Software: IDEA
# @python version: 3.7.4
"""

import os
from datetime import datetime

from .common.http_client import HttpClient


class Translate:
    # 镜像版本号，默认值
    def_version = "0.2"
    # 镜像容器端口，默认值
    def_port = "30002"
    # 镜像名称，默认值
    def_name = "translate"

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def trans_text(self, from_lang, to_lang, text, is_merge, output=None):
        """
        文本翻译
        :param from_lang: 源语言，非空,zh-CN:中文、en-英文、de-德文、ja-日文等(参考谷歌翻译)，必选参数
        :param to_lang: 目标语言，非空,zh-CN:中文、en-英文、de-德文、ja-日文等(参考谷歌翻译)，必选参数
        :param text: 正文，必选参数
        :param is_merge: 是否合并返回，默认合并返回，可选参数。
        :return:
            合并返回：String

        """
        http_client = HttpClient()
        url = "http://" + self.ip + ":" + str(self.port) + "/translate/trans"

        data = {
            "from": from_lang,
            "to": to_lang,
            "text": text,
            "isMerge": is_merge
        }
        dt = http_client.post(url, arg_type="data", **data)

        result = dt["data"]
        if output:
            create_time = datetime.strftime(datetime.now(), "%Y%m%d%H%M%S%f")
            txt_name = "translate_" + create_time + ".txt"
            save_path = os.path.join(output, txt_name)
            with open(save_path, "w", encoding="utf-8") as fw:
                fw.write(result)

        return result

    def trans_file(self, from_lang, to_lang, file_path, is_merge, output=None):
        """
        文本翻译
        :param from_lang: 源语言，非空,zh-CN:中文、en-英文、de-德文、ja-日文等(参考谷歌翻译)，必选参数
        :param to_lang: 目标语言，非空,zh-CN:中文、en-英文、de-德文、ja-日文等(参考谷歌翻译)，必选参数
        :param file_path: 输入文件路径，必选参数
        :param is_merge: 是否合并返回，默认合并返回，可选参数。
        :param output: 结果保存为文件的保存路径，可选参数。
        :return:
            合并返回：String 例如：People's Republic of China
            非合并返回： [{'src': '中华人民共和国', 'target': "People's Republic of China"}]
        """

        #f = open(file_path, "r", encoding='utf-8')
        text = ""
        with open(file_path,'r',encoding='utf-8') as f:
            text = f.read()

        # print("text:" + text)
        return self.trans_text(from_lang, to_lang, text, is_merge,output);

if __name__ == '__main__':
    print("start")


