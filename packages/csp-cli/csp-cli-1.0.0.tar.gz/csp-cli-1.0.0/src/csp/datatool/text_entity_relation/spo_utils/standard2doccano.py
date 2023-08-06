#!/usr/bin/env python
# -*- coding:utf-8 -*-
# authors: zhys513
# Date: 2020-06-22
# desc : 标准格式转百度doccano标注（SPO）
import json
import os
import sys
import click

usage = "python standard2doccano.py --standard_path ./data/standard --output ./data/"


data_connection_category = []
data_label_category = []
data_source = []
data_label = []
data_connection = []
dict_label_category = {}
dict_connection_category = {} 


# @click.command()
# @click.option("--standard_path", prompt="your standard labels file path(json)", help='eg: data/standard',
#               type=str)
# @click.option("--output",  prompt="whrer to save output result",
#               help='File path for saving evaluation results.eg:data', type=str)
def standard2doccno(standard_path, output): 
    label_category_path = os.path.join(standard_path,"labelCategories.json")
    source_path = os.path.join(standard_path,"sources.json")
    label_path = os.path.join(standard_path,"labels.json")
    connection_path = os.path.join(standard_path,"connections.json")
    connection_category_path = os.path.join(standard_path,"connectionCategories.json") 
 
    if not check_input_file([label_category_path, source_path, label_path, connection_path,connection_category_path]):
        sys.exit(1)
 
    os.makedirs(output,exist_ok=True) 

    data_proc(label_category_path, source_path, label_path, connection_category_path, connection_path)
    series_doccano = get_doccano()
 
    file_name = "standard2doccano_ext.json"

    output_item = os.path.join(output, file_name)    
    with open(output_item, "w", encoding="utf-8") as f:
        for item in series_doccano: 
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    
    relations,schema_dict = gen_relation()
    
    write_json(relations,standard_path,"relations.json") 
    
    write_json(schema_dict,standard_path,"schema.json",0) 


def write_json(data, output, file_name,indent=4):
    output_item = os.path.join(output, file_name)  
    with open(output_item, "w", encoding="utf-8") as f: 
        f.write(json.dumps(data, ensure_ascii=False, indent=indent))
     
def read_json(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

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

def data_proc(label_category_path, source_path, label_path, connection_category_path=None, connection_path=None):
    """
    数据预处理
    对原始数据读取和转换
    并赋值全局变量
    """
    global data_label_category, data_connection_category, data_source, data_label, data_connection,id2labelCategory,id2connectionCategorie
    data_label_category = read_json(label_category_path)
    if connection_category_path:
        data_connection_category = read_json(connection_category_path)
    data_source = read_json(source_path)
    data_label = read_json(label_path)
    if connection_path:
        data_connection = read_json(connection_path) 
        
    id2labelCategory = {str(row['id']):row['text'] for row in data_label_category} 
    id2connectionCategorie = {str(row['id']):row['text'] for row in data_connection_category} 


def get_doccano():
    """
    主程序
    数据组装
    """
    series = []
    for source in data_source:
        result = {}

        text_id = str(source["id"])   
        result["id"] = int(source["id"])
        result["text"] = source["content"].replace('\r\n','**') 

        result["entities"] = get_labels(text_id) 
        result["relations"] = get_connections(text_id)

        series.append(result)
    return series 

def get_labels(text_id):
    """
    组装实体数据
    """
    labels = []
    for label in data_label:
        result_label = {"id": int(label["id"])}
        srcId = str(label["srcId"])
        if text_id == srcId:
            label_category = id2labelCategory[str(label["categoryId"])]
            result_label["label"] = label_category
            # result_label["name"] = label["name"]
            result_label["start_offset"] = int(label["startIndex"])
            result_label["end_offset"] = int(label["endIndex"])
            labels.append(result_label)
    return labels 


def get_connections(text_id):    
    """
    组装关系数据
    """
    if data_connection:
        connections = []
        for connection in data_connection:
            result_connection = {"id": int(connection["id"])}
            srcId = str(connection["srcId"])
            if text_id == srcId:
                connection_category = id2connectionCategorie[str(connection["categoryId"])]
                result_connection["type"] = connection_category
                result_connection["from_id"] = int(connection["fromId"])
                result_connection["to_id"] = int(connection["toId"])
                connections.append(result_connection)
    else:
        connections = []

    return connections
 

def gen_relation():  
    '''
    生成 实体-关系-实体 集
    方便其他格式转回 公司标注数据格式
    '''
    #转数据
    relations = [] 
    str_relations = [] 
    schema_dict = {}
    labels2id = {row['srcId'] + str(row['id']):row for row in data_label} 
    labelCategories_dict = {str(row['id']):row['text'] for row in data_label_category}
    connectionCategories_dict = {str(row['id']):row['text'] for row in data_connection_category}
    for row in data_connection: 
        srcId = row['srcId']
        categoryId = row['categoryId']
        fromId = srcId + str(row['fromId']) 
        toId = srcId + str(row['toId'])
        # 获取实体类型ID
        from_categoryId = labels2id[fromId]['categoryId']
        to_categoryId = labels2id[toId]['categoryId']
        str_relation = str(categoryId)+str(to_categoryId)+str(from_categoryId) 
        if str_relation in str_relations:
            continue
        relations.append({
            "categoryId": categoryId,
            "toId": to_categoryId,
            "fromId": from_categoryId
            })
        str_relations.append(str_relation) 
         
        
        # 获取关系类型
        category = connectionCategories_dict[str(categoryId)] 
        # 获取实体类型
        from_category = labelCategories_dict[str(from_categoryId)] 
        to_category = labelCategories_dict[str(to_categoryId)] 
        print({
            "fromId": from_category,
            "categoryId": category,
            "toId": to_category
            })
        
        subs = schema_dict.get(from_category)
        if subs:
            subs.append(category)
            subs = list(set(subs))
            schema_dict[from_category] = subs
        else:
            schema_dict[from_category] = [category] 
    
    print("schema:\n",schema_dict)
    return relations,schema_dict
  
if __name__ == '__main__':  
    # standard2doccno() 
    print("SUCCESS")
    
    standard_path = "./data/standard"
    output = "./data/"
    standard2doccno(standard_path, output)
