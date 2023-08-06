#!/usr/bin/env python
# encoding: utf-8
import click,os 
from csp.pipeline.pipeline_cli import pipeline


@pipeline.group("uie")
def uie():
    """
    csp pipeline uie Command line
    """

@uie.command() 
@click.option("--test_data_path",'-t', help="test_data_path:待提取csv数据，格式为，id:唯一id,content:待抽取的文本", default='data/source/new.csv',type=str)
@click.option("--relation_path",'-r', help="relation_path:人工梳理的三亚组关系，格式:[{'relation': '参与', 'to_label': '会议', 'from_label': '单位' }]'"
              ,default=os.path.join('output/uie/','relations.json'),type=str)
@click.option("--max_seq_len",'-l', help="max_seq_len:待抽取文本序列长度，默认512:",default=512 , type=int)
@click.option("--checkpoint",'-c', help="checkpoint:微调后的模型地址，不填时使用UIE自带通用模型:", default="",type=str)
@click.option("--model",'-m', help="model:UIE使用模型:", default='uie-tiny',type=str)
@click.option("--size",'-s', help="size:待抽取个数，默认为0，代表全部抽取:", default=0 , type=int)
@click.option("--retain",'-re', help="retain:保留未抽取到的id和content:", default=True , type=bool)
def spo(test_data_path,relation_path,max_seq_len,checkpoint,model, size,retain):
    from  csp.pipeline.uiepipe.predict import extract
    extract(test_data_path,relation_path ,max_seq_len,checkpoint,model, size,retain)
    

@uie.command() 
@click.option("--batch_size", default=16, type=int, help="Batch size per GPU/CPU for training.")
@click.option("--learning_rate", default=1e-5, type=float, help="The initial learning rate for Adam.")
@click.option("--train_path", default='output/uie/train.txt', type=str, help="The path of train set.")
@click.option("--dev_path", default='output/uie/dev.txt', type=str, help="The path of dev set.")
@click.option("--save_dir", default='./checkpoint', type=str, help="The output directory where the model checkpoints will be written.")
@click.option("--max_seq_len", default=512, type=int, help="The maximum input sequence length. "
    "Sequences longer than this will be truncated, sequences shorter will be padded.")
@click.option("--num_epochs", default=100, type=int, help="Total number of training epochs to perform.")
@click.option("--seed", default=1000, type=int, help="Random seed for initialization")
@click.option("--logging_steps", default=10, type=int, help="The interval steps to logging.")
@click.option("--valid_steps", default=100, type=int, help="The interval steps to evaluate model performance.")
@click.option('--device',  default="gpu", help="Select which device to train model, defaults to gpu.") # choices=['cpu', 'gpu'],
@click.option("--model",  default="uie-base", type=str, help="Select the pretrained model for few-shot learning.") # choices=["uie-base", "uie-tiny", "uie-medical-base"],
@click.option("--init_from_ckpt", default=None, type=str, help="The path of model parameters for initialization.")
def finetune(batch_size,learning_rate,train_path,dev_path,save_dir,max_seq_len,
             num_epochs,seed,logging_steps,valid_steps,device,model,init_from_ckpt):
    from  csp.pipeline.uiepipe.finetune import do_train 
    do_train(batch_size,learning_rate,train_path,dev_path,save_dir,max_seq_len,
             num_epochs,seed,logging_steps,valid_steps,device,model,init_from_ckpt)
    

@uie.command() 
@click.option("--doccano_file", default="output/uie/doccano_ext.json", type=str, help="The doccano file exported from doccano platform.")
@click.option("--save_dir", default="output/uie", type=str, help="The path of data that you wanna save.")
@click.option("--negative_ratio", default=5, type=int, help="Used only for the classification task, the ratio of positive and negative samples, number of negtive samples = negative_ratio * number of positive samples")
@click.option("--splits", default=[0.8, 0.1, 0.1], nargs=3,type=float, help="The ratio of samples in datasets. [0.6, 0.2, 0.2] means 60% samples used for training, 20% for evaluation and 20% for test.") # nargs="*", 
@click.option("--task_type", default="ext", type=str, help="Select task type, ext for the extraction task and cls for the classification task, defaults to ext.") # choices=['ext', 'cls'], 
@click.option("--options", default=["正向", "负向"], nargs=2,type=str,help="Used only for the classification task, the options for classification") #  nargs="+", 
@click.option("--prompt_prefix", default="情感倾向", type=str, help="Used only for the classification task, the prompt prefix for classification")
@click.option("--is_shuffle", default=True, type=bool, help="Whether to shuffle the labeled dataset, defaults to True.")
@click.option("--seed", type=int, default=1000, help="random seed for initialization")
def doccano(doccano_file,save_dir,negative_ratio,splits,task_type,options,prompt_prefix,is_shuffle,seed): 
    from  csp.pipeline.uiepipe.doccano import do_convert
    do_convert(doccano_file,save_dir,negative_ratio,splits,task_type,options,prompt_prefix,is_shuffle,seed)


@uie.command() 
@click.option("--model_path", type=str, default='checkpoint/model_best', help="The path of saved model that you want to load.")
@click.option("--test_path", type=str, default='output/uie/test.txt', help="The path of test set.")
@click.option("--batch_size", type=int, default=16, help="Batch size per GPU/CPU for training.")
@click.option("--max_seq_len", type=int, default=512, help="The maximum total input sequence length after tokenization.")
@click.option("--model", type=str, default="uie-base", help="Specify the pretrained model.") #choices=["uie-base", "uie-tiny", "uie-medical-base"], 
def evaluate(model_path,test_path,batch_size,max_seq_len,model): 
    from  csp.pipeline.uiepipe.evaluate import do_eval
    do_eval(model_path,test_path,batch_size,max_seq_len,model)
    