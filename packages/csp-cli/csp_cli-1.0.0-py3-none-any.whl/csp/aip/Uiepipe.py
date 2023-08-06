#!/usr/bin/env python
# encoding: utf-8  

class Uiepipe: 
    def __init__(self): 
        pass
     
    def spo(self,
            test_data_path='data/source/test.csv',
            relation_path='output/uie/relations.json',
            max_seq_len=512,
            checkpoint='',
            model= 'uie-base' , 
            size=0,
            retain=False
            ):
        '''
        基于UIE的三元组抽取
        Args:
            test_data_path : test_data_path:待提取csv数据，格式为，id:唯一id,content:待抽取的文本
            relation_path : relation_path:人工梳理的三亚组关系，格式:[{'relation': '参与', 'to_label': '会议', 'from_label': '单位' }]'
            max_seq_len : 待抽取文本序列长度，默认512
            checkpoint : 微调后的模型地址，不填时使用UIE自带通用模型
            model : UIE使用模型 默认 'uie-base'
            size : 待抽取个数，默认为0，代表全部抽取
            retain : 保留未抽取到的id和content
        Returns:
        '''
        from  csp.pipeline.uiepipe.predict import extract
        extract(test_data_path,relation_path ,max_seq_len,checkpoint,model, size,retain)


    def finetune(self,
                 train_path='output/uie/train.txt',
                 dev_path='output/uie/dev.txt',
                 batch_size=16,
                 max_seq_len=512,
                 num_epochs=100,
                 learning_rate=1e-5,
                 save_dir='checkpoint',
                 seed=1000,
                 logging_steps=10,
                 valid_steps=100,
                 device="gpu",
                 model="uie-base",
                 init_from_ckpt=None
                 ):
        '''
        基于UIE的三元组抽取模型训练
        Args:
            batch_size : Batch size per GPU/CPU for training.
            learning_rate : The initial learning rate for Adam.
            train_path : The path of train set.
            dev_path : The path of dev set.
            save_dir : The output directory where the model checkpoints will be written.
            max_seq_len : The maximum input sequence length. 
            num_epochs : Total number of training epochs to perform.
            seed : Random seed for initialization.
            logging_steps : The interval steps to logging.
            valid_steps : The interval steps to evaluate model performance.
            device : Select which device to train model, defaults to gpu.
            model : Select the pretrained model for few-shot learning.
            init_from_ckpt :The path of model parameters for initialization.
        Returns:
        '''
        from csp.pipeline.uiepipe.finetune import do_train 
        do_train(batch_size,learning_rate,train_path,dev_path,save_dir,max_seq_len,
                 num_epochs,seed,logging_steps,valid_steps,device,model,init_from_ckpt)
         

    def doccano(self,
                doccano_file="output/uie/doccano_ext.json",
                save_dir="output/uie",
                negative_ratio=5,
                splits=[0.8, 0.1, 0.1],
                task_type="ext",
                options=["正向", "负向"],
                prompt_prefix="情感倾向",
                is_shuffle=False,
                seed=1000
                ): 
        '''
        doccano标注数据转换&&比例分割为UIE训练数据、验证数据和测试数据
        Args:
            doccano_file : The doccano file exported from doccano platform.")
            save_dir : The path of data that you wanna save.")
            negative_ratio : Used only for the classification task, the ratio of positive and negative samples, number of negtive samples = negative_ratio * number of positive samples.
            splits : The ratio of samples in datasets. [0.6, 0.2, 0.2] means 60% samples used for training, 20% for evaluation and 20% for test.
            task_type : Select task type, ext for the extraction task and cls for the classification task, defaults to ext.
            options : Used only for the classification task, the options for classification.
            prompt_prefix : Used only for the classification task, the prompt prefix for classification.
            is_shuffle : Whether to shuffle the labeled dataset, defaults to True.
            seed : random seed for initialization. 
        Returns:
        '''        
        from  csp.pipeline.uiepipe.doccano import do_convert
        do_convert(doccano_file,save_dir,negative_ratio,splits,task_type,options,prompt_prefix,is_shuffle,seed)


    def evaluate(self,
                 model_path='checkpoint/model_best',
                 test_path='output/uie/test.txt',
                 batch_size=16,
                 max_seq_len=512,
                 model="uie-base"
                 ): 
        '''
        UIE训练结果预测评估
        Args:
            model_path : The path of saved model that you want to load.
            test_path : The path of test set.
            batch_size : Batch size per GPU/CPU for training.
            max_seq_len : The maximum total input sequence length after tokenization.
            model : Specify the pretrained model.
        Returns:
        '''       
        from  csp.pipeline.uiepipe.evaluate import do_eval
        do_eval(model_path,test_path,batch_size,max_seq_len,model)

if __name__ == '__main__':
    print("start")


