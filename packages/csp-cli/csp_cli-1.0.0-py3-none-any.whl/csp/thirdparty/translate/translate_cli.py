#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/7/01 15:50
# @Author  : liny
# @Site    :
# @File    : Translate_cli.py
# @Software: IDEA
# @python version: 3.7.4
"""

import click
from csp.command.cli import csptools
from csp.thirdparty import Translate

# 一级命令 CSP translate
@csptools.group("translate")
def translate():
    """
    Translation tools, supporting multiple languages
    """

## 文本翻译
@translate.command()
@click.option("-v", "--version", help="the version of server images", default=None)
@click.option("-p", "--port", help="the port for server container", default=None)
@click.option("-c", "--c_name", help="the container name", default=None)
@click.option('-r', is_flag=True, help="Re query image information.Indicates true when it appears")
@click.option("-f", "--from_lang", help="Source language, non-empty, zh-CN: Chinese, en-English, de-German, ja-Japanese, etc. ", required=True)
@click.option("-t", "--to_lang", help="Target language, not empty, zh-CN: Chinese, en-English, de-German, ja-Japanese, etc.", required=True)
@click.option("-i", "--text", help="input text to translate", required=True)
@click.option("-m", "--is_merge", help="whether to merge the return, otherwise return the source and target",  default=None)
@click.option("-o", "--output", help="the folder to save output txt file", default=None)
def trans_text(version, port, c_name, r, from_lang, to_lang, text , is_merge,output):
    """
    Text translation, support for multiple languages
    """
    translateclient = Translate(version=version, port=port, c_name=c_name, reload=r)

    result = translateclient.trans_text(from_lang,to_lang,text,is_merge,output)
    print(result)


## 中文翻译为英文
@translate.command()
@click.option("-v", "--version", help="the version of server images", default=None)
@click.option("-p", "--port", help="the port for server container", default=None)
@click.option("-c", "--c_name", help="the container name", default=None)
@click.option('-r', is_flag=True, help="Re query image information.Indicates true when it appears")
@click.option("-i", "--text", help="input text to translate", required=True)
@click.option("-m", "--is_merge", help="whether to merge the return, otherwise return the source and target",  default=None)
@click.option("-o", "--output", help="the folder to save output txt file", default=None)
def text_cn_to_en(version, port, c_name, r, text , is_merge, output):
    """
    Text translation, Chinese to English translation
    """
    translateclient = Translate(version=version, port=port, c_name=c_name, reload=r)

    result = translateclient.trans_text_cn_to_en(text,is_merge,output)
    print(result)

## 英文翻译为中文
@translate.command()
@click.option("-v", "--version", help="the version of server images", default=None)
@click.option("-p", "--port", help="the port for server container", default=None)
@click.option("-c", "--c_name", help="the container name", default=None)
@click.option('-r', is_flag=True, help="Re query image information.Indicates true when it appears")
@click.option("-i", "--text", help="input text to translate", required=True)
@click.option("-m", "--is_merge", help="whether to merge the return, otherwise return the source and target",  default=None)
@click.option("-o", "--output", help="the folder to save output txt file", default=None)
def text_en_to_cn(version, port, c_name, r, text , is_merge, output):
    """
    Text translation, English to Chinese translation
    """
    translateclient = Translate(version=version, port=port, c_name=c_name, reload=r)

    result = translateclient.trans_text_en_to_cn(text,is_merge,output)
    print(result)

## 文件翻译
@translate.command()
@click.option("-v", "--version", help="the version of server images", default=None)
@click.option("-p", "--port", help="the port for server container", default=None)
@click.option("-c", "--c_name", help="the container name", default=None)
@click.option('-r', is_flag=True, help="Re query image information.Indicates true when it appears")
@click.option("-f", "--from_lang", help="Source language, non-empty, zh-CN: Chinese, en-English, de-German, ja-Japanese, etc. ", required=True)
@click.option("-t", "--to_lang", help="Target language, not empty, zh-CN: Chinese, en-English, de-German, ja-Japanese, etc.", required=True)
@click.option("-i", "--file_path", help="input file path to translate", required=True)
@click.option("-m", "--is_merge", help="whether to merge the return, otherwise return the source and target",  default=None)
@click.option("-o", "--output", help="the folder to save output txt file", default=None)
def trans_file(version, port, c_name, r, from_lang, to_lang, file_path , is_merge,output):
    """
    File translation, support for multiple languages
    """
    translateclient = Translate(version=version, port=port, c_name=c_name, reload=r)

    result = translateclient.trans_file(from_lang,to_lang,file_path,is_merge,output)
    print(result)


## 中文翻译为英文
@translate.command()
@click.option("-v", "--version", help="the version of server images", default=None)
@click.option("-p", "--port", help="the port for server container", default=None)
@click.option("-c", "--c_name", help="the container name", default=None)
@click.option('-r', is_flag=True, help="Re query image information.Indicates true when it appears")
@click.option("-i", "--file_path", help="input file path to translate", required=True)
@click.option("-m", "--is_merge", help="whether to merge the return, otherwise return the source and target",  default=None)
@click.option("-o", "--output", help="the folder to save output txt file", default=None)
def file_cn_to_en(version, port, c_name, r, file_path , is_merge, output):
    """
    File translation, Chinese to English translation
    """
    translateclient = Translate(version=version, port=port, c_name=c_name, reload=r)

    result = translateclient.trans_file_cn_to_en(file_path,is_merge,output)
    print(result)

## 英文翻译为中文
@translate.command()
@click.option("-v", "--version", help="the version of server images", default=None)
@click.option("-p", "--port", help="the port for server container", default=None)
@click.option("-c", "--c_name", help="the container name", default=None)
@click.option('-r', is_flag=True, help="Re query image information.Indicates true when it appears")
@click.option("-i", "--file_path", help="input file path to translate", required=True)
@click.option("-m", "--is_merge", help="whether to merge the return, otherwise return the source and target",  default=None)
@click.option("-o", "--output", help="the folder to save output txt file", default=None)
def file_en_to_cn(version, port, c_name, r, file_path , is_merge, output):
    """
    File translation, English to Chinese translation
    """
    translateclient = Translate(version=version, port=port, c_name=c_name, reload=r)

    result = translateclient.trans_file_en_to_cn(file_path,is_merge,output)
    print(result)