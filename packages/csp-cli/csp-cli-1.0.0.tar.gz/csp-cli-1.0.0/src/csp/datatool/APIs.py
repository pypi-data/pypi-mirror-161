#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/5/24 9:26
# @Author  : xgy
# @Site    : 
# @File    : Unst2st.py
# @Software: PyCharm
# @python version: 3.7.4
"""
import os

from csp.datatool.image_classify.aug import img_classify_aug
from csp.datatool.image_classify.check import img_classify_check
from csp.datatool.image_classify.eda import img_classify_eda
from csp.datatool.image_classify.eva import img_classify_eva
from csp.datatool.image_classify.split import img_classify_split
from csp.datatool.image_classify.transform import img_classify_transform
from csp.datatool.image_detection.aug import det_aug
from csp.datatool.image_detection.check import det_check
from csp.datatool.image_detection.eda import det_eda
from csp.datatool.image_detection.eva import det_eva
from csp.datatool.image_detection.split import det_split
from csp.datatool.image_detection.transform import det_transform
from csp.datatool.text_classify.check import text_classify_check
from csp.datatool.text_classify.eda import text_classify_eda
from csp.datatool.text_classify.eva import text_classify_eva
from csp.datatool.text_classify.split import text_classify_split
from csp.datatool.text_entity.check import entity_check
from csp.datatool.text_entity.eda import entity_eda
from csp.datatool.text_entity.eva import entity_eva
from csp.datatool.text_entity.split import entity_split
from csp.datatool.text_entity_relation.check import spo_check
from csp.datatool.text_entity_relation.eda import spo_eda
from csp.datatool.text_entity_relation.split import spo_split
# from csp.datatool.text_entity_relation.eva import spo_eva
from csp.datatool.text_entity_relation.spo_eva import spo_eva
from csp.datatool.text_entity_relation.transform import spo_transform
from csp.datatool.utils import task_l


# 按任务类型，整合数据集处理 API


def task_check(name):
    if name not in task_l:
        raise KeyError("task should be one of {}".format(task_l))


# 数据集切分
def split(data_dir, task, ratio: float, form=None, mode=None):
    task_check(task)
    if task == "obj_det":
        det_split(folder=data_dir, form=form, ratio=ratio, mode=mode)
    elif task == "text_entity_extra":
        entity_split(folder=data_dir, ratio=ratio)
    elif task == "text_entity_relation_extra":
        spo_split(folder=data_dir, ratio=ratio)
    elif task == "img_cls":
        img_classify_split(folder=data_dir, ratio=ratio)
    elif task == "text_cls":
        text_classify_split(folder=data_dir, ratio=ratio)


# 数据集转换
def transform(data_dir, task, form=None, output=None, uie_file=None):
    task_check(task)
    if task == "obj_det":
        det_transform(folder=data_dir, form=form, output=output)
    elif task == "text_entity_relation_extra":
        spo_transform(folder=data_dir, form=form, output=output, uie_file=uie_file)
    elif task == "img_cls":
        img_classify_transform(folder=data_dir, output=output)


# 数据集检查
def check(data_dir, task, form=None, output=None):
    task_check(task)
    if output and not os.path.exists(output):
        os.makedirs(output, exist_ok=True)
    if task == "obj_det":
        if not form:
            raise IOError("-f/--form cannot be empty")
        det_check(folder=data_dir, form=form, output=output)
    elif task == "text_entity_extra":
        entity_check(folder=data_dir, output=output)
    elif task == "text_entity_relation_extra":
        spo_check(folder=data_dir, output=output)
    elif task == "img_cls":
        img_classify_check(folder=data_dir, output=output)
    elif task == "text_cls":
        text_classify_check(folder=data_dir, output=output)


# 预测结果评估
def eva(submit_file, gold_file, task, origin_image_dir=None, long_text_categories=None, output=None):
    task_check(task)
    if output and not os.path.exists(output):
        os.makedirs(output, exist_ok=True)
    if task == "obj_det":
        if not os.path.isfile(gold_file) and not os.path.isfile(submit_file):
            raise FileNotFoundError("In task 'obj_det' gold_file  and submit_file should be a file")
        det_eva(submit_file, gold_file, origin_image_dir=origin_image_dir, output_dir=output)
    elif task == "text_entity_extra":
        if not os.path.isdir(gold_file):
            raise FileNotFoundError("In task 'text_entity_extra' gold_file should be a folder")
        entity_eva(submit_file, gold_file, long_text_categories, output=output)
    elif task == "text_entity_relation_extra":
        if not os.path.isdir(submit_file) or not os.path.isdir(gold_file):
            raise FileNotFoundError("In task 'text_entity_relation_extra' submit_file and gold_file should be a folder")
        spo_eva(submit_file, gold_file, output=output)
    elif task == "img_cls":
        if not os.path.isdir(gold_file):
            raise FileNotFoundError("In task 'img_cls' gold_file should be a folder")
        img_classify_eva(submit_file, gold_file, output=output)
    elif task == "text_cls":
        if not os.path.isdir(gold_file):
            raise FileNotFoundError("In task 'text_cls' gold_file should be a folder")
        text_classify_eva(submit_file, gold_file, output=output)


# 数据集分析
def eda(data_dir, task, output, form=None):
    task_check(task)
    if task == "obj_det":
        det_eda(data_dir, form, output)
    elif task == "text_entity_extra":
        entity_eda(data_dir, output)
    elif task == "text_entity_relation_extra":
        spo_eda(data_dir, output)
    elif task == "img_cls":
        img_classify_eda(data_dir, output)
    elif task == "text_cls":
        text_classify_eda(data_dir, output)


# 数据集增强
def aug(data_dir, task, aug_config, mode=None):
    task_check(task)
    if task == "obj_det":
        det_aug(data_dir, aug_config, mode)
    if task == "img_cls":
        img_classify_aug(data_dir, aug_config)


if __name__ == '__main__':
    print("start")
