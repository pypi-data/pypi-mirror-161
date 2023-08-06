#!/usr/bin/env python
# -*- coding: utf-8 -*-
# desc: 零样本启动步骤1：预测
# 功能描述：针对三元组关系，使用UIE进行零样本启动，获取结果，并可以转换为doccano和标准格式
  
import os,json,uuid
from tqdm import tqdm

OUTPUT_UIE_PATH = 'output/uie/'

os.makedirs(OUTPUT_UIE_PATH,exist_ok = True)

def gen_id():
    '''
    使用UUID生成唯一ID
    '''
    return str(uuid.uuid4().int)[:10]
      
def gen_schema(relation_path):
    '''
    转换为UIE三元组抽取关系schema
    :param relation_path :
     relation 示例: [{ 
            "relation": "参与",
            "to_label": "会议",
            "from_label": "单位"
            }]
    '''
    # todo 判断relation_path不能为空
    schema = {}
    labelCategories = []
    connectionCategories = []
    labelCategorie2id = {}
    connectionCategorie2id = {} 
    
    schema2toLabel = {}
    with open(relation_path, "r+", encoding="utf-8") as f:
        data = json.load(f) 
        for row in data:
            from_label = row['from_label'] 
            to_label = row['to_label']
            relation = row['relation'] 
            relations = schema.get(from_label)
            # 存在关系
            if relations:
                relations.append(relation)
                relations = list(set(relations))
                schema[from_label] = relations 
            else: 
                schema[from_label] = [relation]
            
            schema2toLabel[from_label + '_' + relation] = to_label
            
            # 判断 categoryId fromId toId 是否存在
            if not row.get('categoryId') or not row.get('fromId') or not row.get('toId'):   
                labelCategories.append(from_label)
                labelCategories.append(to_label)
                connectionCategories.append(relation) 
            else:
                labelCategorie2id[row['from_label']] = row['fromId']
                labelCategorie2id[row['to_label']] = row['toId']
                connectionCategorie2id[row['relation']] = row['categoryId']
        
        # 只要存在 id 不全就重新生成
        if not labelCategorie2id or not connectionCategorie2id:
            #重定文本指针位置
            f.seek(0)
            f.truncate()
            relations_ids = []
            labelCategories = list(set(labelCategories))
            connectionCategories = list(set(connectionCategories))
            labelCategorie2id = {categorie : str(i * 10 + 1) for i,categorie in enumerate(labelCategories)}
            connectionCategorie2id = {categorie : str(i * 10 + 2) for i,categorie in enumerate(connectionCategories)}
            for row in data:
                from_label = row['from_label']
                relation = row['relation']  
                to_label = row['to_label']
                row['fromId'] = labelCategorie2id[from_label]
                row['categoryId'] = connectionCategorie2id[relation]
                row['toId'] = labelCategorie2id[to_label]
                relations_ids.append(row)
        
            f.write(json.dumps(relations_ids, ensure_ascii=False, indent=4)) 
            
            
    return schema,labelCategorie2id,connectionCategorie2id,schema2toLabel

def predict(test_datas:list, schema,checkpoint,model="uie-base",max_seq_len=512,size=0):
    """
    预测，直接保存所有预测结果,默认保存至output/uie
    :param test_datas: [{id:'',content:''}]
    :param schema: UIE关系抽取schema
    :param size : 有效数据的数据量 0:代表使用全部数据
    :param max_seq_len:带预测文本序列长度
    :param checkpoint: 微调后的模型地址 
    :return:
    """  
    from paddlenlp import Taskflow
    datas = []  
    output_file = os.path.join(OUTPUT_UIE_PATH,"uie_spo_predict.json")
    with open(output_file, "w", encoding="utf-8") as f: 
        
        if checkpoint or len(checkpoint) <= 0 :
            ie = Taskflow('information_extraction',schema=schema,model=model,max_seq_len=max_seq_len)
        else:  
            ie = Taskflow('information_extraction', schema=schema,model=model,task_path=checkpoint,max_seq_len=max_seq_len)
                
        if size > 0 and len(test_datas) >= size:
            test_datas = test_datas[:size]
            
        for _, row in tqdm(enumerate(test_datas)):
            content = str(row['content'])
            labels = ie(content) 
            data = {
                'id': str(row['id']),
                'content': content,
                'labels': labels
            }
            datas.append(data)
            f.write(json.dumps(data, ensure_ascii=False) + "\n") 

    print(f'finish.predict result save to:{output_file}')
    
    return datas,output_file
  
def read_jsons(filename):
    '''读取单个txt文件，文件中包含多行，返回[json]'''
    datas = []
    with open(filename, encoding='utf-8') as f:
        txts = f.readlines()
        for txt in txts:
            data_json = json.loads(txt.strip('\n'))
            datas.append(data_json)
    return datas 

def write_file(data, output, file_name):
    os.makedirs(output,exist_ok = True)
    output_file = os.path.join(output, file_name)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f'write_file  finish, file save to:{output_file}') 
     
def uiespo2doccano(relation_path,predict_result_file,retain=True): 
    result = read_jsons(predict_result_file)
    output_file = os.path.join(OUTPUT_UIE_PATH,"doccano_pred.json") 
    datas = [] 
    with open(output_file, "w", encoding="utf-8") as f: 
        _,_,_,schema2toLabel = gen_schema(relation_path) 
        for rs in result: 
            data = {}
            series_label = []
            series_connection = []
            
            srcId = str(rs["id"])
            data['id'] = srcId
            data['text'] = rs['content']
            labels = rs["labels"] 
            for label in labels:
                for from_label in label.keys(): 
                    dlist = label[from_label]
                    for entity in dlist: 
                        start = entity["start"]
                        end = entity["end"] 
                        probability = entity["probability"]  
                        if probability > 0.5:
                            fromId = gen_id()
                            result = {"id": fromId,
                                      "label": from_label,
                                      "start_offset": start,
                                      "end_offset": end 
                                      } 
                            # 添加实体
                            series_label.append(result)
                            relations = entity.get("relations")
                            if relations:
                                for stype in relations.keys():  
                                    for entity in relations[stype]: 
                                        start = entity["start"]
                                        end = entity["end"]  
                                        toId = gen_id()
                                        result = {"id": toId,
                                                  "label": schema2toLabel[from_label + '_' + stype],
                                                  "start_offset": start,
                                                  "end_offset": end 
                                                  } 
                                        # 添加实体
                                        series_label.append(result) 
                                    
                                    # 处理 三元组
                                    series_connection.append({    
                                        "id": gen_id(),     
                                        "type": stype, 
                                        "to_id": toId ,
                                        "from_id": fromId}) 
                                    
            
            if retain or (not retain and series_connection):   
                data['entities'] = series_label            
                data['relations'] = series_connection   
                f.write(json.dumps(data, ensure_ascii=False) + "\n")   
                datas.append(data)  
    
    print(f'extract  finish, doccano file save to:{output_file}')
    
    return datas,output_file

def doccano2standard(relation_path,doccano_file):  
    sources = []
    labels = []
    labelCategories = []
    connectionCategories = []
    connections = []
    _,labelCategorie2id,connectionCategorie2id,_ = gen_schema(relation_path) 
    doccano_jsons = read_jsons(doccano_file)
    for data in doccano_jsons:
        strId = data['id']
        content = data['text'] 
        sources.append({
            'id':strId,
            'title':strId,
            'content':content
            })
        
        entities = data['entities'] 
        for ent in entities: 
            labelId = labelCategorie2id[ent['label']]
            startIndex = ent['start_offset']
            endIndex = ent['end_offset']
            labels.append({
                "id": ent['id'],
                "srcId": strId,
                "categoryId": labelId,
                "name": content[startIndex:endIndex],
                "startIndex": startIndex,
                "endIndex": endIndex
            })
        
        relations = data['relations'] 
        for rel in relations:  
            categorieId = connectionCategorie2id[rel['type']]
            connections.append({
                "id": rel['id'],
                "srcId": strId,
                "categoryId": categorieId,
                "fromId": rel['from_id'],
                "toId": rel['to_id']
            })
            
    for  text,lid in labelCategorie2id.items():
        labelCategories.append({
            "id": lid,
            "text": text
        })
        
    for  text,lid in connectionCategorie2id.items():
        connectionCategories.append({
            "id": lid,
            "text": text
        }) 
    
    output_path = os.path.join(OUTPUT_UIE_PATH,'standard')  
    write_file(sources,output_path,"sources.json")
    write_file(labels,output_path,"labels.json")
    write_file(labelCategories,output_path,"labelCategories.json")
    write_file(connectionCategories,output_path,"connectionCategories.json")
    write_file(connections,output_path,"connections.json")
    
    return output_path


import pandas as pd
# import click  
# @click.command()
# @click.option("--test_data_path",'-t', prompt="test_data_path:待提取csv数据，格式为，id:唯一id,content:待抽取的文本", default='data/source/new.csv',type=str)
# @click.option("--relation_path",'-r', prompt="relation_path:人工梳理的三亚组关系，格式:[{'relation': '参与', 'to_label': '会议', 'from_label': '单位' }]'"
#               ,default=os.path.join(OUTPUT_UIE_PATH,'relations.json'),type=str)
# @click.option("--max_seq_len",'-l', help="max_seq_len:待抽取文本序列长度，默认512:",default=512 , type=int)
# @click.option("--checkpoint",'-c', help="checkpoint:微调后的模型地址，不填时使用UIE自带通用模型:", default='',type=str)
# @click.option("--model",'-m', help="model:UIE使用模型:", default='uie-tiny',type=str)
# @click.option("--size",'-s', help="size:待抽取个数，默认为0，代表全部抽取:", default=20 , type=int)
# @click.option("--retain",'-re', help="retain:保留未抽取到的id和content:", default=True , type=bool)
def extract(test_data_path,relation_path ='output/uie/relations.json',max_seq_len=512,checkpoint='',model = 'uie-base' , size=0,retain=True):
    """
    抽取三元组信息，载入待抽取数据，依据定义的relations.json获取uie schema
    默认生成地址为output/uie
    :param test_data_path : 待提取csv数据，格式为，id:唯一id,content:待抽取的文本
    :param relation_path : 定义的关系信息
    :param max_seq_len : 抽取文本序列长度
    :param checkpoint : 微调后的模型地址，不填时使用UIE自带通用模型
    :param size : 有效数据的数据量 0:代表使用全部数据
    :return:
    """
    schema,_,_,_ = gen_schema(relation_path) 
    print('schema =',schema) 
     
    # 将数据集构造成 [{id:"",content:""}]格式
    df_test = pd.read_csv(test_data_path,header=0,encoding="utf-8")
    test_datas = []
    for _,row in df_test.iterrows():
        test_datas.append(row) 
         
    print('test_datas[0]:',test_datas[0])
    
    _,predict_result_file = predict(test_datas=test_datas, schema=schema,max_seq_len=max_seq_len,checkpoint = checkpoint,model=model,size=size)
    _,doccano_file = uiespo2doccano(relation_path,predict_result_file,retain)
    doccano2standard(relation_path,doccano_file)
            
if __name__ == '__main__': 
    extract()
