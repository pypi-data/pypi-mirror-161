#!/usr/bin/env python
# -*- coding:utf-8 -*-
# authors: zhys513
# Date: 2020-06-22
# desc : UIE推理结果转换为标准格式（SPO）

import json
import os
import sys
import shutil
# import click

usage = "python uiespo2standard.py --spo_file data/uiespo.json --label_categories_path data/standard/labelCategories.json --connection_categories_path data/standard/connectionCategories.json --relations_path data/standard/relations.json --output data/uiespo2standard"


# def uiespo2standard(spo_file,label_categories_path,connection_categories_path,relations_path, output):
def uiespo2standard(uie_file, ori_folder, output):
    spo_file = uie_file
    ori_folder = ori_folder
    label_categories_path = os.path.join(ori_folder, "labelCategories.json")
    connection_categories_path = os.path.join(ori_folder, "connectionCategories.json")
    relations_path = os.path.join(ori_folder, "relations.json")

    result_json = {}
    if not os.path.exists(spo_file):
        result_json["error_code"] = 1001
        result_json["error_msg"] = ("未找到待转换的标注数据工具数据文件 %s" % spo_file)
        print(json.dumps(result_json, ensure_ascii=False))
        sys.exit(1)

    if not check_input_file([spo_file, label_categories_path, connection_categories_path, relations_path]):
        sys.exit(1)
 
    os.makedirs(output, exist_ok=True)

    data_proc(label_categories_path, relations_path, connection_categories_path)
    
    
    data_spo = read_txts(spo_file)
      
    series_source = get_source(data_spo) 
    series_label,series_connection = get_label_connection(data_spo)
    
    file_label_category = "labelCategories" + ".json"
    file_connection_category = "connectionCategories" + ".json"
    file_source = "sources" + ".json"
    file_label = "labels" + ".json"
    file_connection = "connections" + ".json"
    file_relation = "relations" + ".json"
 
    copy_file(label_categories_path,output, file_label_category)
    copy_file(connection_categories_path,output, file_connection_category)
    copy_file(relations_path,output, file_relation)
    
    write_file(series_source, output, file_source)
    write_file(series_label, output, file_label)
    if series_connection:
        write_file(series_connection, output, file_connection)

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
     
def data_proc(labelCategories_path, relations_path, connectionCategories_path):
    """
    数据预处理
    对原始数据读取和转换
    并赋值全局变量
    """
    global data_label_category, data_connection_category, data_relations,labelCategory2id,id2labelCategory,connectionCategorie2id,id2connectionCategorie,relation2id
    data_label_category = read_json(labelCategories_path)
    data_connection_category = read_json(connectionCategories_path)
    data_relations = read_json(relations_path)  
    
    labelCategory2id = {row['text']:row['id'] for row in data_label_category} 
    id2labelCategory = {row['id']:row['text'] for row in data_label_category} 
    connectionCategorie2id = {row['text']:row['id'] for row in data_connection_category} 
    id2connectionCategorie = {row['id']:row['text'] for row in data_connection_category} 
    
    relation2id = {str(row['fromId'] + str(row['categoryId'])):row['toId'] for row in data_relations} 
    
    
def read_json(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def read_txts(filename):
    '''读取单个txt文件，文件中包含多行，返回[json]'''
    datas = []
    with open(filename, encoding='utf-8') as f:
        txts = f.readlines()
        for txt in txts:
            data_json = json.loads(txt.strip('\n'))
            datas.append(data_json)
    return datas
        
def get_source(data_spo):
    series_source = []
    for item in data_spo:
        result = {"id": item["id"],
                  "title": item["id"],
                  "content": item["content"]}
        series_source.append(result)
    return series_source


def get_label_connection(data_spo):
    '''转换获取实体集[]和关系集[]'''
    series_label = []
    series_connection = []
    for tag in data_spo:
        srcId = str(tag["id"])
        labels = tag["labels"]
        # text = tag["content"] 
        labelid = 0
        for label in labels:
            for key in label.keys():
                labelCategoryId = labelCategory2id[key]
                dlist = label[key]
                for entity in dlist:
                    name = entity['text']
                    start = entity["start"]
                    end = entity["end"]
                    labelid = labelid + 1
                    fromId = labelid
                    result = {"id": fromId,
                              "srcId": srcId,
                              "categoryId": labelCategoryId
                              }
    
                    result["name"] = name
                    result["startIndex"] = start
                    result["endIndex"] = end
                    # 添加实体
                    series_label.append(result)
                    relations = entity.get("relations")
                    if relations:
                        for key in relations.keys(): 
                            connectionCategorieId = connectionCategorie2id[key]
                            for entity in relations[key]: 
                                name = entity['text']
                                start = entity["start"]
                                end = entity["end"] 
                                labelid = labelid + 1
                                toId = labelid 
                                relationId = relation2id[str(labelCategoryId) + str(connectionCategorieId)]
                                result = {"id": toId,
                                          "srcId": srcId,
                                          "categoryId": relationId
                                          }
                                
                                result["name"] = name
                                result["startIndex"] = start
                                result["endIndex"] = end
                                # 添加实体
                                series_label.append(result) 
                            
                            # 处理 三元组
                            series_connection.append({    
                                "srcId": srcId,
                                "id": labelid,     
                                "categoryId": connectionCategorieId,
                                "toId": toId ,
                                "fromId": fromId})  

    return series_label,series_connection


def get_connection_category(data_spo):    
    """
    组装关系标签数据
    """
    data = data_spo[0]
    series_connection_category = []
    connectionCategories = data["connectionCategories"]
    for item in connectionCategories:
        result = {"id": item["id"], "text": item["text"]}
        series_connection_category.append(result)
    return series_connection_category


def get_connection(data_spo):
    """
    组装关系数据
    """
    series_connection = []
    for tag in data_spo:
        srcId = str(tag["id"])
        connections = tag["connections"]
        if connections:
            for connection in connections:
                result = {"id": connection["id"],
                          "srcId": srcId,
                          "categoryId": connection["categoryId"],
                          "fromId": connection["fromId"],
                          "toId": connection["toId"]}
                series_connection.append(result)

    return series_connection


def write_file(data, output, file_name):
    file_path = os.path.join(output, file_name)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def copy_file(src_file,output, file_name):
    file_path = os.path.join(output, file_name)
    shutil.copy(src_file,file_path)

if __name__ == '__main__':
    print("SUCCESS")
    uiespo2standard()
    # uiespoFile = "./data/uiespo.json"  
    # labelCategories_path = "./data/standard/labelCategories.json"   
    # connectionCategories_path = "./data/standard/connectionCategories.json"
    # relations_path = './data/standard/relations.json'
    # output = "./data/uiespo2standard" 
    # uiespo2standard(uiespoFile,labelCategories_path,connectionCategories_path,relations_path, output)
 