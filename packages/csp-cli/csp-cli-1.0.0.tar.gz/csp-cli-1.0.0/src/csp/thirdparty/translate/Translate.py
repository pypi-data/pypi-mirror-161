#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/7/01 15:50
# @Author  : liny
# @Site    :
# @File    : Translate.py
# @Software: IDEA
# @python version: 3.7.4
"""
import csp.aip.Translate
from csp.common.docker_server import DockerServer

class Translate:
    # 镜像版本号，默认值
    def_version = "0.2"
    # 镜像容器端口，默认值
    def_port = "30002"
    # 镜像名称，默认值
    def_name = "translate"

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
        self.http_sdk = csp.aip.Translate(ip="127.0.0.1", port=self.port)

        # self.port = port
        self.server = DockerServer(name=self.name, version=self.version, port=self.port, c_name=c_name, reload=reload)
        self.server.start()

    def trans_text(self, from_lang, to_lang, text, is_merge=None, output=None):
        """
        文本翻译
        :param from_lang: 源语言，非空,zh-CN:中文、en-英文、de-德文、ja-日文等(参考谷歌翻译)，必选参数
        :param to_lang: 目标语言，非空,zh-CN:中文、en-英文、de-德文、ja-日文等(参考谷歌翻译)，必选参数
        :param text: 正文，必选参数
        :param is_merge: 是否合并返回，默认合并返回，可选参数。
        :param output: 结果保存为文件的保存路径，可选参数。
        :return:
            合并返回：String 例如：People's Republic of China
            非合并返回： [{'src': '中华人民共和国', 'target': "People's Republic of China"}]
        """
        result = self.http_sdk.trans_text(from_lang, to_lang, text, is_merge,output);
        return result

    def trans_text_cn_to_en(self,text, is_merge=None, output=None):
        """
        文本翻译-中文翻译为英文
        :param text: 正文，必选参数
        :param is_merge: 是否合并返回，默认合并返回，可选参数。
        :param output: 结果保存为文件的保存路径，可选参数。
        :return:
            合并返回：String 例如：People's Republic of China
            非合并返回： [{'src': '中华人民共和国', 'target': "People's Republic of China"}]
        """
        result = self.http_sdk.trans_text("zh-CN", "en", text, is_merge, output);
        return result

    def trans_text_en_to_cn(self,text, is_merge=None, output=None):
        """
        文本翻译-英文翻译为中文
        :param text: 正文，必选参数
        :param is_merge: 是否合并返回，默认合并返回，可选参数。
        :param output: 结果保存为文件的保存路径，可选参数。
        :return:
            合并返回：String 例如：People's Republic of China
            非合并返回： [{'src': '中华人民共和国', 'target': "People's Republic of China"}]
        """
        result = self.http_sdk.trans_text("en", "zh-CN", text, is_merge, output);
        return result

    def trans_file(self, from_lang, to_lang, file_path, is_merge=None, output=None):
        """
        文件翻译
        :param from_lang: 源语言，非空,zh-CN:中文、en-英文、de-德文、ja-日文等(参考谷歌翻译)，必选参数
        :param to_lang: 目标语言，非空,zh-CN:中文、en-英文、de-德文、ja-日文等(参考谷歌翻译)，必选参数
        :param file_path: 输入文件路径，必选参数
        :param is_merge: 是否合并返回，默认合并返回，可选参数。
        :param output: 结果保存为文件的保存路径，可选参数。
        :return:
            合并返回：String 例如：People's Republic of China
            非合并返回： [{'src': '中华人民共和国', 'target': "People's Republic of China"}]
        """
        result = self.http_sdk.trans_file(from_lang, to_lang, file_path, is_merge,output);
        return result

    def trans_file_cn_to_en(self,file_path, is_merge=None, output=None):
        """
        文件翻译-中文翻译为英文
        :param file_path: 输入文件路径，必选参数
        :param is_merge: 是否合并返回，默认合并返回，可选参数。
        :param output: 结果保存为文件的保存路径，可选参数。
        :return:
            合并返回：String 例如：People's Republic of China
            非合并返回： [{'src': '中华人民共和国', 'target': "People's Republic of China"}]
        """
        result = self.http_sdk.trans_file("zh-CN", "en", file_path, is_merge, output);
        return result

    def trans_file_en_to_cn(self,file_path, is_merge=None, output=None):
        """
        文件翻译-英文翻译为中文
        :param file_path: 输入文件路径，必选参数text: 正文，必选参数
        :param is_merge: 是否合并返回，默认合并返回，可选参数。
        :param output: 结果保存为文件的保存路径，可选参数。
        :return:
            合并返回：String 例如：People's Republic of China
            非合并返回： [{'src': '中华人民共和国', 'target': "People's Republic of China"}]
        """
        result = self.http_sdk.trans_file("en", "zh-CN", file_path, is_merge, output);
        return result

if __name__ == '__main__':
    print("start")
    translate = Translate()
    text = "中华人民共和国";
    # result = translate.trans_text("zh-CN", "en",text);
    #result = translate.trans_text_cn_to_en(text);
    # print("translate result :", result);
    result = translate.trans_text_en_to_cn("People's Republic of China");
    print("translate result :", result);

    # filePath= "/Users/liny/test.txt"
    # outputPath = "/Users/liny/";
    # result = translate.trans_file_en_to_cn( filePath, None ,outputPath);
    #print("translate result :", result);