#!/usr/bin/env python
# encoding: utf-8
import click,os 
from csp.pipeline.pipeline_cli import pipeline

from  csp.pipeline.uiepipe.predict import extract,OUTPUT_UIE_PATH

@pipeline.group("uie")
def uie():
    """
    csp pipeline uie Command line
    """

@uie.command() 
@click.option("--test_data_path",'-t', prompt="test_data_path:待提取csv数据，格式为，id:唯一id,content:待抽取的文本", default='data/source/new.csv',type=str)
@click.option("--relation_path",'-r', prompt="relation_path:人工梳理的三亚组关系，格式:[{'relation': '参与', 'to_label': '会议', 'from_label': '单位' }]'"
              ,default=os.path.join(OUTPUT_UIE_PATH,'relations.json'),type=str)
@click.option("--max_seq_len",'-l', help="max_seq_len:待抽取文本序列长度，默认512:",default=512 , type=int)
@click.option("--checkpoint",'-c', help="checkpoint:微调后的模型地址，不填时使用UIE自带通用模型:", default='',type=str)
@click.option("--model",'-m', help="model:UIE使用模型:", default='uie-tiny',type=str)
@click.option("--size",'-s', help="size:待抽取个数，默认为0，代表全部抽取:", default=0 , type=int)
@click.option("--retain",'-re', help="retain:保留未抽取到的id和content:", default=True , type=bool)
def spo(test_data_path,relation_path ='output/uie/relations.json',max_seq_len=512,checkpoint='',model = 'uie-base' , size=0,retain=True):
    extract(test_data_path,relation_path ,max_seq_len,checkpoint,model, size,retain)
    

def finetune(): 
    pass
    
