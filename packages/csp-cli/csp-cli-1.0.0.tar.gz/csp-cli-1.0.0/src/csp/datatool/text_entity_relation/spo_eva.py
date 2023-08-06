#!/usr/bin/env python
# -*- coding:utf-8 -*-
# authors: chenjianghai
# Date: 2020-08-22
#
#
import json
import os
import sys
import click
import pandas as pd

usage = "python spo_eva.py --submit_path  data/submit --eva_path data/eva --output data"


# @click.command()
# @click.option('--submit_path', prompt="your submit labels file path(json)", help='eg: data/submit',
#               type=str)
# @click.option('--eva_path', prompt="labels category file path(json)", help='eg: data/eva',
#               type=str)
# @click.option('--output', prompt="whrer to save output result",
#               help='File path for saving evaluation results.eg:data', type=str)

def spo_eva(submit_path,eva_path,output):
    conn_category_file = os.path.join(submit_path,'connectionCategories.json')
    lables_category_file = os.path.join(submit_path,'labelCategories.json')
    submit_conn_file = os.path.join(submit_path,'connections.json')
    submit_entity_file = os.path.join(submit_path,'labels.json') 
     
    eva_conn_file = os.path.join(eva_path,'connections.json')
    eva_entity_file = os.path.join(eva_path,'labels.json') 

    evaluate(submit_entity_file, submit_conn_file, eva_entity_file, eva_conn_file, lables_category_file,
             conn_category_file, output)
    

def evaluate(submit_entity_file, submit_conn_file, eva_entity_file, eva_conn_file, lables_category_file,
             conn_category_file, output):
    if not check_input_file([submit_entity_file, submit_conn_file, eva_entity_file, eva_conn_file, lables_category_file,
                             conn_category_file]):
        sys.exit(1)

    submit_entity_df = pd.read_json(submit_entity_file, orient='recodes')
    eva_entity_df = pd.read_json(eva_entity_file, orient='recodes')
    entity_categorg_dict = dict_category(lables_category_file)
    print("all label catalog：" + json.dumps(entity_categorg_dict, ensure_ascii=False))
    entity_eva_result, entity_eva_total = eva_entity(entity_categorg_dict, submit_entity_df, eva_entity_df)

    submit_conn_df = pd.read_json(submit_conn_file, orient='recodes')
    eva_conn_df = pd.read_json(eva_conn_file, orient='recodes')
    conn_category_dict = dict_category(conn_category_file)
    print("all connections catalog：" + json.dumps(conn_category_dict, ensure_ascii=False))
    submit_entity_id_name_dict = get_entity_id_name_dict(submit_entity_df)
    eva_entity_id_name_dict = get_entity_id_name_dict(eva_entity_df)
    conn_eva_result, conn_eva_total = eva_connections(conn_category_dict, submit_conn_df, eva_conn_df,
                                                      submit_entity_id_name_dict, eva_entity_id_name_dict)

    total = eva_total(entity_eva_total, conn_eva_total)
    series = []
    for s in entity_eva_result:
        series.append(s)
    series.append(entity_eva_total)
    for s in conn_eva_result:
        series.append(s)
    series.append(conn_eva_total)
    series.append(total)
    df_result = pd.DataFrame(data=series)
    df_result = df_result[['precision', 'recall', 'f_score', 'type', 'category']]
    df_result['precision'] = df_result['precision'].apply(lambda x:round(x,6))
    df_result['recall'] = df_result['recall'].apply(lambda x:round(x,6))
    df_result['f_score'] = df_result['f_score'].apply(lambda x:round(x,6))
     
    # df_result = df_result[['precision', 'recall', 'accuracy', 'f_score', 'type', 'column', 'category']]
    print(df_result)
    # df_result = df_result.sort_values(by="f_score", ascending=False)

    os.makedirs(output,exist_ok = True) 
    output = os.path.join(output,"result.csv")
    df_result.to_csv(output, index=False, sep="\t", encoding="utf-8")
    print('evaluate finish')


def eva_entity(entity_categorg_dict, submit_entity_file, eva_entity_df):
    eva_result_series = []
    final_accuracy = 0
    final_precision = 0
    final_recall = 0
    final_f_score = 0
    for catalogId in entity_categorg_dict:
        submit_values = get_entity_values(catalogId, submit_entity_file)
        labeld_values = get_entity_values(catalogId, eva_entity_df)
        accuracy, precision, recall = calculate_entity(submit_values, labeld_values)
        final_accuracy += accuracy
        final_precision += precision
        final_recall += recall
        if precision == 0 and recall == 0:
            f_score = 0
        else:
            f_score = 2 * precision * recall / (precision + recall)
        final_f_score += f_score
        eva_result_series.append(
            {'column': catalogId,
             'accuracy': accuracy,
             'precision': precision,
             'recall': recall,
             'f_score': f_score,
             "category": entity_categorg_dict[catalogId], 'type': '实体'})

    final_accuracy = round(final_accuracy / len(entity_categorg_dict), 6)
    final_precision = round(final_precision / len(entity_categorg_dict), 6)
    final_recall = round(final_recall / len(entity_categorg_dict), 6)
    final_f_score = round(final_f_score / len(entity_categorg_dict), 6)
    entity_eva_total = {'column': 'entity_total', 'accuracy': final_accuracy, 'precision': final_precision,
                        'recall': final_recall,
                        'f_score': final_f_score, "category": '实体汇总', 'type': '实体'}
    return eva_result_series, entity_eva_total


def eva_connections(conn_category_dict, submit_conn_df, eva_conn_df, submit_entity_id_name_dict,
                    eva_entity_id_name_dict):
    eva_result_series = []
    final_accuracy = 0
    final_precision = 0
    final_recall = 0
    final_f_score = 0
    for catalogId in conn_category_dict:
        submit_values = get_connections_values(catalogId, submit_entity_id_name_dict, submit_conn_df)
        labeld_values = get_connections_values(catalogId, eva_entity_id_name_dict, eva_conn_df)
        accuracy, precision, recall = calculate_conn(submit_values, labeld_values)
        final_accuracy += accuracy
        final_precision += precision
        final_recall += recall
        if precision == 0 and recall == 0:
            f_score = 0
        else:
            f_score = 2 * precision * recall / (precision + recall)
        final_f_score += f_score
        eva_result_series.append(
            {'column': catalogId,
             'accuracy': accuracy,
             'precision': precision,
             'recall': recall,
             'f_score': f_score,
             "category": conn_category_dict[catalogId], 'type': '关系'})

    final_accuracy = round(final_accuracy / len(conn_category_dict), 6)
    final_precision = round(final_precision / len(conn_category_dict), 6)
    final_recall = round(final_recall / len(conn_category_dict), 6)
    final_f_score = round(final_f_score / len(conn_category_dict), 6)
    entity_total = {'column': 'entity_total', 'accuracy': final_accuracy, 'precision': final_precision,
                    'recall': final_recall,
                    'f_score': final_f_score, "category": '关系汇总', 'type': '关系'}
    return eva_result_series, entity_total


def eva_total(entity_eva_total, conn_eva_total):
    accuracy = (entity_eva_total['accuracy'] + conn_eva_total['accuracy']) / 2
    precision = (entity_eva_total['precision'] + conn_eva_total['precision']) / 2
    recall = (entity_eva_total['recall'] + conn_eva_total['recall']) / 2
    f_score = (entity_eva_total['f_score'] + conn_eva_total['f_score']) / 2
    return {'column': 'total', 'accuracy': accuracy, 'precision': precision,
            'recall': recall, 'f_score': f_score, "category": '汇总', 'type': '汇总'}


def dict_category(category_path):
    df = pd.read_json(category_path, orient='recodes')
    ret_dict = {}
    for index, row in df.iterrows():
        id = str(row['id'])
        text = str(row['text'])
        ret_dict[id] = text
    return ret_dict


def check_input_file(file_path_arr):
    for file_path in file_path_arr:
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            print_error_msg(("指定的文件路径不存在: %s" % file_path), 1001)
            return False
    return True


def print_error_msg(msg, code):
    result_json = {}
    result_json['error_msg'] = msg
    result_json['error_code'] = code
    result_json['usage'] = usage
    print(json.dumps(result_json, ensure_ascii=False))


class EntityInfo(object):
    """
    实体信息
    """

    def __init__(self, srcId, catalogId, labelValue, startIndex, endIndex):
        self.srcId = srcId
        self.catalogId = catalogId
        self.labelValue = labelValue
        self.endIndex = endIndex
        self.startIndex = startIndex
        
    def get_key(self):
        return "_".join([str(self.srcId),str(self.catalogId),str(self.startIndex),str(self.endIndex),str(self.labelValue)])

class ConnectionInfo(object):
    """
    关系信息
    """

    def __init__(self, srcId, fromName, toName, connCatalogId):
        self.srcId = srcId
        self.fromName = fromName
        self.toName = toName
        self.connCatalogId = connCatalogId 

    def get_key(self):
        return str(self.srcId) + '_' + str(self.fromName) + "_" + str(self.toName) + "_" + str(self.connCatalogId)
    
def calculate_entity(y_pred, y_true):
    """
    计算某一个类别的accuracy, precision, recall
    :param y_pred:
    :param y_true:
    :return:
    """
    tp_count = 0
    true_dict = {}
    true_id_labelds_dict = {}
    for EntityInfo in y_true:  
        key = EntityInfo.get_key()
        true_dict[key] = key
        sub_arr = []
        if EntityInfo.srcId in true_id_labelds_dict:
            sub_arr = true_id_labelds_dict[EntityInfo.srcId]
        sub_arr.append(EntityInfo.labelValue)
        true_id_labelds_dict[EntityInfo.srcId] = sub_arr
    
    EntityInfoKeys = [] # 去重，同一个实体不能重复计算
    for EntityInfo in y_pred:
        key = EntityInfo.get_key()
        if key in true_dict and key not in EntityInfoKeys:
            tp_count += 1
            EntityInfoKeys.append(key)
    if len(y_pred) == 0 or len(y_true) == 0:
        return 0, 0, 0

    precision = round(tp_count / len(y_pred), 6)
    recall = round(tp_count / len(y_true), 6)
    accuracy = precision

    return accuracy, precision, recall


def calculate_conn(y_pred, y_true):
    tp_count = 0
    true_dict = {}
    for connInfo in y_true:
        key = connInfo.get_key()
        true_dict[key] = key

    for connInfo in y_pred:
        key = connInfo.get_key()
        if key in true_dict:
            tp_count += 1
    if len(y_pred) == 0 or len(y_true) == 0:
        return 0, 0, 0

    precision = round(tp_count / len(y_pred), 6)
    recall = round(tp_count / len(y_true), 6)
    accuracy = precision

    return accuracy, precision, recall


def get_entity_values(catalogId, df):
    """
    得到指定catalogId的实体标注信息
    :param catalogId:
    :param df:
    :return:
    """

    values = []
    # label_value_dict = {}
    for index, row in df.iterrows():
        name = str(row['name'])
        if str(row['categoryId']) == catalogId:
            key = str(row['srcId']) + "_" + name
            # if key in label_value_dict:
            #     continue
            label = EntityInfo(row['srcId'], catalogId, name, row['startIndex'], row['endIndex'])
            values.append(label)
            # label_value_dict[key] = key
    return values


def get_connections_values(catalogId, entity_id_name_dict, df):
    """
    得到指定catalogId的关系标注信息
    :param catalogId:
    :param df:
    :return:
    """

    values = []
    for index, row in df.iterrows():
        if str(row['categoryId']) == catalogId:
            src_id = str(row['srcId'])
            from_id = str(row['fromId'])
            to_id = str(row['toId'])
            from_entity_name = entity_id_name_dict[src_id + "_" + to_id]
            to_entity_name = entity_id_name_dict[src_id + "_" + from_id]
            conn = ConnectionInfo(row['srcId'], from_entity_name, to_entity_name, str(row['categoryId']))
            values.append(conn)
    return values


def get_entity_id_name_dict(df):
    """
    获取实体结果中的id跟name的dict（便于后续关系评估中判断）
    :param df:
    :return: 关系dict，key为srcId_id ,value:实体名称
    """
    id_name_dict = {}
    for index, row in df.iterrows():
        id = str(row['id'])
        src_id = str(row['srcId'])
        name = str(row['name'])
        id_name_dict[src_id + "_" + id] = name

    return id_name_dict


if __name__ == '__main__':
    spo_eva()
    print("SUCCESS")
    # submit_path = "data/uiespo2standard"
    # eva_path = "data/standard"
    # outpath = "data"
    # spo_eva(submit_path,eva_path,outpath)
