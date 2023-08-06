# Copyright (c) 2022 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
 
from functools import partial

import paddle
from paddlenlp.datasets import load_dataset
from paddlenlp.transformers import AutoTokenizer
from paddlenlp.metrics import SpanEvaluator

from csp.pipeline.uiepipe.model import UIE
from csp.pipeline.uiepipe.utils import convert_example, reader, MODEL_MAP


@paddle.no_grad()
def evaluate(model, metric, data_loader):
    """
    Given a dataset, it evals model and computes the metric.
    Args:
        model(obj:`paddle.nn.Layer`): A model to classify texts.
        metric(obj:`paddle.metric.Metric`): The evaluation metric.
        data_loader(obj:`paddle.io.DataLoader`): The dataset loader which generates batches.
    """
    model.eval()
    metric.reset()
    for batch in data_loader:
        input_ids, token_type_ids, att_mask, pos_ids, start_ids, end_ids = batch
        start_prob, end_prob = model(input_ids, token_type_ids, att_mask,
                                     pos_ids)
        start_ids = paddle.cast(start_ids, 'float32')
        end_ids = paddle.cast(end_ids, 'float32')
        num_correct, num_infer, num_label = metric.compute(start_prob, end_prob,
                                                           start_ids, end_ids)
        metric.update(num_correct, num_infer, num_label)
    precision, recall, f1 = metric.accumulate()
    model.train()
    return precision, recall, f1

# import click  
# @click.command()
# @click.option("--model_path", type=str, default=None, help="The path of saved model that you want to load.")
# @click.option("--test_path", type=str, default=None, help="The path of test set.")
# @click.option("--batch_size", type=int, default=16, help="Batch size per GPU/CPU for training.")
# @click.option("--max_seq_len", type=int, default=512, help="The maximum total input sequence length after tokenization.")
# @click.option("--model", choices=["uie-base", "uie-tiny", "uie-medical-base"], type=str, default="uie-base", help="Specify the pretrained model.")
def do_eval(model_path,test_path,batch_size,max_seq_len,model):
    encoding_model = MODEL_MAP[model]['encoding_model']

    tokenizer = AutoTokenizer.from_pretrained(encoding_model)
    model = UIE.from_pretrained(model_path)

    test_ds = load_dataset(
        reader,
        data_path=test_path,
        max_seq_len=max_seq_len,
        lazy=False)
    test_ds = test_ds.map(
        partial(
            convert_example, tokenizer=tokenizer, max_seq_len=max_seq_len))

    test_batch_sampler = paddle.io.BatchSampler(
        dataset=test_ds, batch_size=batch_size, shuffle=False)
    test_data_loader = paddle.io.DataLoader(
        dataset=test_ds, batch_sampler=test_batch_sampler, return_list=True)

    metric = SpanEvaluator()
    precision, recall, f1 = evaluate(model, metric, test_data_loader)
    print("Evaluation precision: %.5f, recall: %.5f, F1: %.5f" %
          (precision, recall, f1))


if __name__ == "__main__":  
    do_eval()
