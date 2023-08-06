#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/6/29 17:24
# @Author  : xgy
# @Site    : 
# @File    : aug.py
# @Software: PyCharm
# @python version: 3.7.4
"""

import math
import os
import threading
import time

import numpy as np
from PIL import Image
from loguru import logger
from tqdm import tqdm

from csp.datatool.image_classify.utils import ImgClassify
from csp.datatool.image_detection.aug import DetAug


class ImgClassifyAug(ImgClassify):

    def __init__(self, data_dir, aug_file=None):
        super(ImgClassifyAug, self).__init__(data_dir)
        self.output = aug_file
        self.det_aug = DetAug(data_dir, aug_file)
        self.imgfiles = []
        self.aug_img_names = []

    def reset_dir(self):
        # 删除增强的图片
        for item in os.listdir(self.img_dir):
            if item.startswith('imgaug_'):
                os.remove(self.img_dir + os.sep + item)

        # 删除增强的标注

        imgfiles = []
        list_n = []
        # 原始文件路径
        path_prefix = None

        with open(self.list_path, "r", encoding="utf-8") as fr:
            anno_l = fr.readlines()

            for item in anno_l:
                item_n = item.replace("\n", "")
                assert len(item.split(" ")) == 2, "标注数据不为两列"

                # 兼容文件路径分隔符
                if "/" in item and "\\\\" not in item:
                    item_split = item_n.split(" ")[0].split("/")
                    file_name = item_split[-1]
                elif "/" not in item and "\\\\" in item:
                    item_split = item_n.split(" ")[0].split("\\\\")
                    file_name = item_split[-1]
                elif "/" in item and "\\\\" in item:
                    item_split = item_n.split(" ")[0].split("\\\\")
                    if "/" in item_split[-1]:
                        item_split = item_split[-1].split("/")
                        file_name = item_split[-1]
                    else:
                        file_name = item_split[-1]
                else:
                    file_name = item_n.split(" ")[0].lstrip(".")
                if not path_prefix:
                    path_prefix = item_n.split(" ")[0].replace(file_name, "")

                if not file_name.startswith('imgaug_'):
                    list_n.append(item.replace("\n", "").replace("\r\n", ""))
                    imgfiles.append([file_name, item_n.split(" ")[1].replace("\n", "").replace("\r\n", "")])
        self.imgfiles = imgfiles
        self.path_prefix = path_prefix
        os.remove(self.list_path)
        with open(self.list_path, "a+", encoding="utf-8") as fw:
            for index, item in enumerate(list_n):
                fw.write(item)
                fw.write("\n")

    def aug(self):
        """
        1. 适用于标准图像分类数据集
        2. 默认对 train_list.txt 包含的文件进行增强
        3. 重新执行增强操作会覆盖上次的操作
        """
        self.reset_dir()
        t1 = time.time()
        if not os.path.exists(self.data_dir):
            raise FileNotFoundError('未能找到相应文件夹，请核查传入的路径')

        trainval_txt_path = self.list_path

        if not self.det_aug.config_dict["basic"]["thread_num"]:
            self.aug_act()  # 未采用多线程
        else:
            self.threading_treat()

        # 生成新的train_list.txt
        with open(trainval_txt_path, "a+", encoding="utf-8") as fw:
            for item in self.aug_img_names:
                if item[0].startswith("imgaug_"):
                    fw.write(self.path_prefix + item[0] + " " + item[1])
                    fw.write("\n")

        print('time cost : %sS' % round(time.time() - t1, 2))

    def aug_act(self):
        """
        图像分类任数据增强不支持背景更换方法
        """

        if self.det_aug.config_dict["basic"]["random"]:
            print('进入随机增强模式')
            aug_methods = [np.random.choice(self.det_aug.methods)]  # 每个xml文件随机选择一种的增强方法
        else:
            print('进入常规增强模式')
            aug_methods = self.det_aug.methods  # 每种所列方法，均进行一次增强操作

        for method_num, aug_method in enumerate(aug_methods):
            for epoch in range(1, self.det_aug.config_dict["basic"]["aug_times"] + 1):
                logger.info("aug using the {} method {} round".format(method_num + 1, epoch))

                for imgfile_l in tqdm(self.imgfiles):
                    imgfile = imgfile_l[0]
                    seq_det = aug_method.to_deterministic()  # 保持坐标和图像同步改变，而不是随机
                    img = Image.open(os.path.join(self.img_dir, imgfile))  # 读取图片
                    img = img.convert('RGB')
                    img = np.array(img)
                    image_aug = seq_det.augment_images([img])[0]
                    new_img_name = 'imgaug_%s_%s_' % (method_num + 1, epoch) + imgfile
                    self.aug_img_names.append([new_img_name, imgfile_l[1]])
                    path = os.path.join(self.img_dir, new_img_name)  # 存储变化后的图片
                    Image.fromarray(image_aug).save(path)

    def threading_treat(self):  # 使用多线程处理，以提升速度
        threads = self.det_aug.config_dict["basic"]["thread_num"]
        if type(threads) == bool:
            threads = os.cpu_count()
        elif type(threads) == int and threads > 0:
            threads = threads
        else:
            raise TypeError("thread_num should be bool or positive int not {}".format(self.det_aug.config_dict["basic"]["thread_num"]))

        print('nums of %s threading are running...' % threads)
        NUMS = len(self.imgfiles)
        num_part = math.ceil(NUMS / threads)  # 计算每个线程要处理的最大数据量
        temp_t = []
        for thread_num in range(threads):
            son_imgfiles = self.imgfiles[num_part * thread_num: num_part * (thread_num + 1)]
            t = threading.Thread(target=self.aug_act, args=())
            temp_t.append(t)
            t.start()
        for t in temp_t:
            t.join()


def img_classify_aug(folder, aug_file=None):
    img_aug = ImgClassifyAug(folder, aug_file)
    img_aug.aug()


if __name__ == '__main__':
    print("start")

