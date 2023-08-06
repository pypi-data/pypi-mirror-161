#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/6/17 9:18
# @Author  : xgy
# @Site    : 
# @File    : eda.py
# @Software: PyCharm
# @python version: 3.7.4
"""
import json
import os
import sys

import click
# import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from loguru import logger

from csp.common.utils import RunSys
from csp.datatool.utils import JsonLoad


class EntityEda:
    """
    文本实体抽取数据集统计分析
    """

    def __init__(self, data_dir, output_dir):
        self.data_dir = data_dir
        self.output_dir = output_dir

        self.label_path = os.path.join(data_dir, 'labels.json')
        self.source_path = os.path.join(data_dir, 'sources.json')
        self.labelcategory_path = os.path.join(data_dir, 'labelCategories.json')

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)

        self.error_msg()

        self.data_labels = JsonLoad(self.label_path).data
        self.data_sources = JsonLoad(self.source_path).data
        self.data_categorys = JsonLoad(self.labelcategory_path).data

    def eda(self):

        series_information, data_text = self.category_information()
        series_chart_len = self.chart_len(data_text)
        # 实体长度75%分位数 total_75
        series_quartile, total_75 = self.chart_quartile(data_text)

        # data_dict = {"information_all": series_information,
        #              "entities_text_len": series_chart_len,
        #              "entities_quartile": series_quartile}
        # self.write_information(data_dict)

        plt.ion()
        self.plot_bar(series_information)
        self.plot_hist(data_text)
        logger.info("the eda results saved in {}".format(self.output_dir))

        # 输出实体总体长度75%分位数、文本长度75%分位数、实体数量至txt文件
        # 其中总体长度75%分位数、文本长度75%分位数最大不能超过512
        # 参数列表
        # 实体数量
        # num_categories = str(len(self.data_categorys))
        # 文本长度75%分位数 source_len_75
        # source_len_75 = self.sources_len()
        # dict_parameter = {"max_seq_length": source_len_75,
        #                   "backoff": total_75,
        #                   "epochs": num_categories}
        # file_name = "eda_parameter.txt"
        # file_path = os.path.join(self.output_dir, file_name)
        # with open(file_path, "w", encoding="utf-8") as fw:
        #     for k, v in dict_parameter.items():
        #         fw.write(v)
        #         fw.write("\n")

    def sources_len(self):
        list_len = []
        for source in self.data_sources:
            len_content = len(source["content"])
            list_len.append(len_content)

        quartiles = np.percentile(list_len, [25, 50, 75])
        source_len_75 = str(quartiles[2])

        return source_len_75

    def category_information(self):
        import pandas as pd

        new_name_list = []

        list_len_max = []
        list_len_min = []
        series_information = []
        text_len = {}
        for category in self.data_categorys:
            result = {}
            category_num = 0
            value_len_all = []
            src_all = []
            category_id = category["id"]
            category_name = category["text"]
            for label in self.data_labels:
                category_value = label["name"]
                category_value_len = len(category_value)
                category_id_label = label["categoryId"]
                src_id = label["srcId"]
                if category_id == category_id_label:
                    category_num += 1
                    value_len_all.append(category_value_len)
                if src_id not in src_all:
                    src_all.append(src_id)

            if not text_len.get(category_name, []):
                text_len[category_name] = value_len_all

            # 定义的实体0标注
            if not value_len_all:
                continue

            result["category_id"] = category_id
            result["category_name"] = category_name
            result["category_num"] = category_num
            result["src_num"] = len(src_all)
            result["len_max"] = max(value_len_all)
            result["len_min"] = min(value_len_all)
            result["len_mean"] = int(np.mean(value_len_all))

            list_len_max.append(max(value_len_all))
            list_len_min.append(min(value_len_all))
            list_len_min.append(int(np.mean(value_len_all)))

            series_information.append(result)
        result_total = {"category_id": len(self.data_categorys),
                        "category_name": "total",
                        "category_num": len(self.data_labels),
                        "src_num": len(self.data_sources),
                        "len_max": max(list_len_max),
                        "len_min": min(list_len_min),
                        "len_mean": int(np.mean(list_len_min))}
        series_information.append(result_total)

        df_information = pd.DataFrame(series_information)
        # print("========实体数据分布概览============")
        # print(df_information)
        output_excel = os.path.join(self.output_dir, "实体数据分布.xlsx")
        df_information.to_excel(output_excel, index=False)

        return series_information, text_len

    # @staticmethod
    def chart_len(self, dict_text):
        import pandas as pd
        series_chart_len = []

        list_len_total = []
        for v in dict_text.values():
            for item in v:
                list_len_total.append(item)
        dict_text["total"] = list_len_total

        for k, v in dict_text.items():
            if not v:
                continue
            len_512 = 0
            len_256 = 0
            len_128 = 0
            len_64 = 0
            len_32 = 0
            len_16 = 0
            len_short = 0
            for len_item in v:
                if len_item >= 512:
                    len_512 += 1
                elif 512 > len_item >= 256:
                    len_256 += 1
                elif 256 > len_item >= 128:
                    len_128 += 1
                elif 128 > len_item >= 64:
                    len_64 += 1
                elif 64 > len_item >= 32:
                    len_32 += 1
                elif 32 > len_item >= 16:
                    len_16 += 1
                else:
                    len_short += 1

            size_category = len(v)
            result = {"category_name": k,
                      "总数": size_category,
                      "512_比例": "%.2f%%" % (len_512 / size_category * 100),
                      "256_比例": "%.2f%%" % (len_256 / size_category * 100),
                      "128_比例": "%.2f%%" % (len_128 / size_category * 100),
                      "64_比例": "%.2f%%" % (len_64 / size_category * 100),
                      "32_比例": "%.2f%%" % (len_32 / size_category * 100),
                      "16_比例": "%.2f%%" % (len_16 / size_category * 100),
                      "小于_16_比例": "%.2f%%" % (len_short / size_category * 100)}
            series_chart_len.append(result)
        df_chart_len = pd.DataFrame(series_chart_len)
        # print("===============实体长度分布表================")
        # print(df_chart_len)
        output_excel = os.path.join(self.output_dir, "实体长度分布.xlsx")
        df_chart_len.to_excel(output_excel, index=False)

        return series_chart_len

    # @staticmethod
    def chart_quartile(self, dict_text):
        import pandas as pd
        series_quartile = []
        del dict_text["total"]

        list_len_total = []
        for v in dict_text.values():
            for item in v:
                list_len_total.append(item)
        dict_text["total"] = list_len_total

        total_75 = None
        for k, v in dict_text.items():
            if not v:
                continue
            quartiles = np.percentile(v, [25, 50, 75])
            size_category = len(v)
            result = {"category_name": k,
                      "总数": size_category,
                      "25%": quartiles[0],
                      "50%": quartiles[1],
                      "75%": quartiles[2],
                      "min": min(v),
                      "max": max(v)}
            series_quartile.append(result)

            if k == "total":
                total_75 = str(quartiles[2])

        df_chart_quartile = pd.DataFrame(series_quartile)
        # print("===============实体长度四分位数分布表===============")
        # print(df_chart_quartile)
        output_excel = os.path.join(self.output_dir, "实体长度四分位数分布.xlsx")
        df_chart_quartile.to_excel(output_excel, index=False)

        return series_quartile, total_75

    # def write_information(self, data_dict):
    #     txt_filename = "data_distribution.txt"
    #     txt_path = os.path.join(self.output_dir, txt_filename)
    #     with open(txt_path, "w+", encoding="utf-8") as fw:
    #         for k, v in data_dict.items():
    #             clo = v[0].keys()
    #             sep = "========================" + k + "========================"
    #             fw.write(sep + "\n")
    #             for index, item in enumerate(clo):
    #                 if index != len(clo) - 1:
    #                     fw.write(item + "\t")
    #                 else:
    #                     fw.write(item + "\n")
    #             for item in v:
    #                 for index, values in enumerate(item.values()):
    #                     if index != len(item.values()) - 1:
    #                         fw.write(str(values) + "\t")
    #                     else:
    #                         fw.write(str(values) + "\n")
    #             fw.write("\n")

    def plot_bar(self, data_plot):
        # import pandas as pd
        # plt.figure(figsize=(15, 15), dpi=200)
        fig, ax1 = plt.subplots(dpi=200)
        ax2 = ax1.twinx()

        df_information = pd.DataFrame(data_plot)
        min_list = df_information['len_min'].tolist()
        del min_list[-1]
        mean_list = df_information['len_mean'].tolist()
        del mean_list[-1]
        max_list = df_information['len_max'].tolist()
        del max_list[-1]
        name_list = df_information['category_name'].tolist()
        del name_list[-1]
        num_list = df_information['category_num'].tolist()
        del num_list[-1]

        ax1.bar(name_list, num_list, label='实体数量', color=['r', 'b', 'g', 'y'])  # , tick_label=name_list
        for x1, yy in zip(name_list, num_list):
            ax1.text(x1, yy + 0.05, str(yy), ha='center', va='bottom', fontsize=10, rotation=0)

        ax2.plot(name_list, min_list, ms=10, label="min")
        ax2.plot(name_list, mean_list, ms=10, label="mean")  # , marker='*'
        ax2.plot(name_list, max_list, ms=10, label="max")
        for y in [min_list, mean_list, max_list]:
            for x1, yy in zip(name_list, y):
                ax2.text(x1, yy + 0.05, str(yy), ha='center', va='bottom', fontsize=10, rotation=0)

        # 并列条形图
        # bar_width = 0.2
        # ax1.bar(x=range(len(name_list)), height=num_list, label='实体数量', color='r', alpha=0.8, width=bar_width)
        # ax2.bar(x=np.arange(len(name_list)) + bar_width, height=min_list,
        #         label='len_min', color='b', alpha=0.8, width=bar_width)
        # ax2.bar(x=np.arange(len(name_list)) + bar_width, height=mean_list,
        #         label='len_mean', color='g', alpha=0.8, width=bar_width)
        # ax2.bar(x=np.arange(len(name_list)) + bar_width, height=max_list,
        #         label='len_max', color='c', alpha=0.8, width=bar_width)

        ax1.set_xlabel('实体类别')
        ax1.set_ylabel('数量', color='g')
        ax2.set_ylabel('文本长度', color='b')

        # plt.xticks(rotation=45)
        # 有标注的标签数量num
        num = len(name_list)
        ax1.set_xticks([i for i in range(0, num)])
        ax1.set_xticklabels(name_list, rotation=45)
        ax1.legend(bbox_to_anchor=(0, 0.9), loc="upper left", borderaxespad=0)
        ax2.legend()

        filename = "category_num_bar.png"
        file_path = os.path.join(self.output_dir, filename)
        plt.savefig(file_path)
        # logger.info("the bar chart has been saved in {}".format(file_path))
        # plt.show()
        # plt.pause(2)

    def plot_hist(self, dict_text):
        plt.figure(figsize=(15, 15), dpi=200)
        plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.5, hspace=0.5)
        size = len(dict_text)
        rows = int(size / 3) + 1
        i = 1
        for k, v in dict_text.items():
            if not v:
                continue
            plt.subplot(rows, 3, i)
            sns.set_palette("hls")
            max_len = max(v)
            min_len = min(v)
            range_len = max_len - min_len
            if range_len == 0:
                space = 10
            elif range_len <= 512:
                space = int(range_len / 1)
            elif 512 < range_len <= 1024:
                space = int(range_len / 10)
            elif range_len > 1024:
                space = int(range_len / 20)
            else:
                space = int(range_len / 40)

            import warnings
            warnings.filterwarnings("ignore")
            # sns.displot()
            sns.distplot(v, bins=space, kde_kws={"color": "seagreen", "lw": 1}, hist_kws={"color": "b"})
            # plt.hist(v, bins=space, histtype='bar', facecolor="blue", edgecolor="black", alpha=0.7, density=True)
            plt.xlabel("文本长度", size=8)
            plt.ylabel("频率", size=8)
            plt.title(k + "频率分布直方图", size=9)
            plt.tick_params(labelsize=7)  # 设置坐标轴刻度字体大小
            i += 1
        filename = "entities_num_density.png"
        file_path = os.path.join(self.output_dir, filename)
        plt.savefig(file_path)
        # logger.info("the hist chart has been saved in {}".format(file_path))
        # plt.show()
        # plt.pause(2)

    def error_msg(self):
        """
        文件存在性检验
        """
        result_json = {}
        if not os.path.isfile(self.labelcategory_path) or not os.path.exists(self.labelcategory_path):
            result_json["error_code"] = 1001
            result_json["error_msg"] = ("未找到实体类别数据labelcategory_path文件 %s" % self.labelcategory_path)
            click.echo(json.dumps(result_json, ensure_ascii=False))
            sys.exit(1)

        if not os.path.isfile(self.source_path) or not os.path.exists(self.source_path):
            result_json["error_code"] = 1002
            result_json["error_msg"] = ("未找到原始数据source文件 %s" % self.source_path)
            click.echo(json.dumps(result_json, ensure_ascii=False))
            sys.exit(1)

        if not os.path.isfile(self.label_path) or not os.path.exists(self.label_path):
            result_json["error_code"] = 1003
            result_json["error_msg"] = ("未找到实体标注数据label文件 %s" % self.label_path)
            click.echo(json.dumps(result_json, ensure_ascii=False))
            sys.exit(1)

        if not os.path.isdir(self.output_dir):
            result_json["error_code"] = 1004
            result_json["error_msg"] = ("output应为文件夹路径 %s" % self.output_dir)
            click.echo(json.dumps(result_json, ensure_ascii=False))
            # os.remove(self.output_dir)
            sys.exit(1)


def entity_eda(data_dir, output):
    # plt.ion()
    # matplotlib.interactive(True)
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    try:
        import pandas as pd
    except ImportError:
        logger.error("there is no pandas try to install it, pip install pandas")
        install_cmd = "pip install pandas"
        RunSys(command=install_cmd).run_cli()

    data_eda = EntityEda(data_dir, output)
    data_eda.eda()
    # 保持图片显示但会阻塞进程，关闭图片后程序继续执行
    # plt.ioff()
    # plt.show()


if __name__ == '__main__':
    print("start")
