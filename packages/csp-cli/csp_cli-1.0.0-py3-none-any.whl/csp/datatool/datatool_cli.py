#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/4/24 10:17
# @Author  : xgy
# @Site    : 
# @File    : datatool_cli.py
# @Software: PyCharm
# @python version: 3.7.4
"""
import click

from csp.command.cli import csptools
from csp.datatool.APIs import aug as data_aug
from csp.datatool.APIs import check as data_check
from csp.datatool.APIs import eda as data_eda
from csp.datatool.APIs import eva as data_eva
from csp.datatool.APIs import split as data_split
from csp.datatool.APIs import transform as data_transform


# 一级命令 CSPtools datatool
@csptools.group("datatool")
def datatool():
    """
    csp datatool Command line \n the tools for dataset,such as checking and transform
    """


## 二级命令
## 数据集切分 split
@datatool.command()
@click.option("-d", "--dir", prompt="the dataset dir", help="the dataset dir", required=True)
@click.option("-t", "--task", type=click.Choice(["obj_det", "img_cls", "text_entity_extra", "text_entity_relation_extra", "text_cls"]),
              prompt="the task type", help="the task type", required=True)
@click.option("-r", "--ratio", type=float, prompt="ratio of training data", help="ratio of training data", required=True)
@click.option("-f", "--form", type=str, help="the dataset type. using in task obj_det it should be voc or coco case insensitive")
@click.option("-m", "--mode", type=click.Choice(['train', 'trainval']), help="identification of data to be split which will work in obj_det", default=None)
def split(dir, task, ratio, form, mode):
    """
    csp datatool split line
    """
    data_split(dir, task, ratio, form=form, mode=mode)


## 二级命令
## 数据集转换 transform
@datatool.command()
@click.option("-d", "--dir", prompt="the dataset dir", help="the dataset dir", required=True)
@click.option("-i", "--uie_file", help="the uie json file that will be required when the task is text_entity_relation_extra and form is uie", default=None)
@click.option("-t", "--task", type=click.Choice(["obj_det", "img_cls", "text_entity_extra", "text_entity_relation_extra"]),
              prompt="the task type", help="the task type", required=True)
@click.option("-f", "--form", type=str, help="the dataset type. In task obj_det it should be voc or coco case insensitive. In task text_entity_relation_extra it should be one of standard2doccano/uie2standard/standard2kg")
@click.option("-o", "--output", prompt="the folder to save out files", help="the folder to save out files", required=True)
def transform(dir, task, form, output, uie_file):
    """
    csp datatool transform line
    """
    data_transform(dir, task, form=form, output=output, uie_file=uie_file)
    print("转换完成")


## 二级命令
## 数据集检查 check
@datatool.command()
@click.option("-d", "--dir", prompt="the dataset dir", help="the dataset dir", required=True)
@click.option("-t", "--task", type=click.Choice(["obj_det", "img_cls", "text_entity_extra", "text_entity_relation_extra", "text_cls"]),
              prompt="the task type", help="the task type", required=True)
@click.option("-f", "--form", type=str, help="using in task obj_det. The dataset type, voc or coco case insensitive", default=None)
@click.option("-o", "--output", help="the folder to save check results", required=True, default="./output")
def check(dir, task, form, output):
    """
    csp datatool check line
    """
    data_check(dir, task, form, output)


## 二级命令
## 预测结果评估 eva
@datatool.command()
@click.option("-i", "--submit_file", prompt="The predict json file. But in task 'text_entity_relation_extra' should be a folder",
              help="The predict json file. But in task 'text_entity_relation_extra' should be a folder", required=True)
@click.option("-g", "--gold_file", prompt="In task 'text_entity_relation_extra'|'text_entity_extra'|'img_cls' should be a folder. In the task 'obj_det' is a json file which type is coco",
              help="In task 'text_entity_relation_extra'|'text_entity_extra'|'img_cls' should be a folder. In the task 'obj_det' is a json file which type is coco", required=True)
@click.option("-t", "--task", type=click.Choice(["obj_det", "text_entity_extra", "img_cls", "text_entity_relation_extra", "text_cls"]),
              prompt="the task type", help="the task type", required=True)
@click.option("-m", "--origin_image_dir", help="the origin image folder, using in obj_det", default=None)
@click.option("-o", "--output", help="the folder to save eva result file", default=None)
@click.argument('long_text_categories', nargs=-1)
def eva(submit_file, gold_file, task, origin_image_dir, long_text_categories, output):
    """
    csp datatool eva line
    """
    data_eva(submit_file, gold_file, task, origin_image_dir=origin_image_dir, long_text_categories=long_text_categories, output=output)


## 二级命令
## 预测结果分析 eda
@datatool.command()
@click.option("-d", "--dir", prompt="the dataset dir", help="the dataset dir", required=True)
@click.option("-t", "--task", type=click.Choice(["obj_det", "img_cls", "text_entity_extra", "text_entity_relation_extra", "text_cls"]),
              prompt="the task type", help="the task type", required=True)
@click.option("-o", "--output", prompt="the folder to save results", help="he folder to save results", default=None)
def eda(dir, task, output):
    """
    csp datatool eda line. only support voc in obj_det
    """
    data_eda(dir, task, output)


## 二级命令
## VOC数据集增强 aug
@datatool.command()
@click.option("-d", "--dir", prompt="the dataset dir, only for VOC", help="the dataset dir, only for VOC", required=True)
@click.option("-t", "--task", type=click.Choice(["obj_det", "img_cls"]),
              prompt="the task type", help="the task type", required=True)
@click.option("-c", "--aug_file", prompt="the yml for imgaug", help="the yml for imgaug", required=True)
@click.option("-m", "--mode", type=click.Choice(['train', 'trainval']), help="identification of data to be aug which will work in obj_det", default=None)
def aug(dir, task, aug_file, mode):
    """
    csp datatool obj_det aug line
    """
    data_aug(dir, task, aug_file, mode)


if __name__ == '__main__':
    print("start")
