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

import os
import time 
import json
import numpy as np

from csp.pipeline.uiepipe.utils import set_seed, convert_ext_examples, convert_cls_examples

# import click  
# @click.command()
# @click.option("--doccano_file", default="./data/standard2doccano_ext.json", type=str, help="The doccano file exported from doccano platform.")
# @click.option("--save_dir", default="./data", type=str, help="The path of data that you wanna save.")
# @click.option("--negative_ratio", default=5, type=int, help="Used only for the classification task, the ratio of positive and negative samples, number of negtive samples = negative_ratio * number of positive samples")
# @click.option("--splits", default=[0.8, 0.1, 0.1], type=float, nargs="*", help="The ratio of samples in datasets. [0.6, 0.2, 0.2] means 60% samples used for training, 20% for evaluation and 20% for test.")
# @click.option("--task_type", choices=['ext', 'cls'], default="ext", type=str, help="Select task type, ext for the extraction task and cls for the classification task, defaults to ext.")
# @click.option("--options", default=["正向", "负向"], type=str, nargs="+", help="Used only for the classification task, the options for classification")
# @click.option("--prompt_prefix", default="情感倾向", type=str, help="Used only for the classification task, the prompt prefix for classification")
# @click.option("--is_shuffle", default=True, type=bool, help="Whether to shuffle the labeled dataset, defaults to True.")
# @click.option("--seed", type=int, default=1000, help="random seed for initialization")
def do_convert(doccano_file,save_dir,negative_ratio,splits,task_type,options,prompt_prefix,is_shuffle,seed):
    set_seed(seed)

    tic_time = time.time()
    if not os.path.exists(doccano_file):
        raise ValueError("Please input the correct path of doccano file.")

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    if len(splits) != 0 and len(splits) != 3:
        raise ValueError("Only []/ len(splits)==3 accepted for splits.")

    if splits and sum(splits) != 1:
        raise ValueError(
            "Please set correct splits, sum of elements in splits should be equal to 1."
        )

    with open(doccano_file, "r", encoding="utf-8") as f:
        raw_examples = f.readlines()

    def _create_ext_examples(examples, negative_ratio=0, shuffle=False):
        entities, relations = convert_ext_examples(examples, negative_ratio)
        examples = [e + r for e, r in zip(entities, relations)]
        if shuffle:
            indexes = np.random.permutation(len(examples))
            examples = [examples[i] for i in indexes]
        return examples

    def _create_cls_examples(examples, prompt_prefix, options, shuffle=False):
        examples = convert_cls_examples(examples, prompt_prefix, options)
        if shuffle:
            indexes = np.random.permutation(len(examples))
            examples = [examples[i] for i in indexes]
        return examples

    def _save_examples(save_dir, file_name, examples):
        count = 0
        save_path = os.path.join(save_dir, file_name)
        with open(save_path, "w", encoding="utf-8") as f:
            for example in examples:
                if task_type == "ext":
                    for x in example:
                        f.write(json.dumps(x, ensure_ascii=False) + "\n")
                        count += 1
                else:
                    f.write(json.dumps(example, ensure_ascii=False) + "\n")
                    count += 1
        print("\nSave %d examples to %s." % (count, save_path))

    if len(splits) == 0:
        if task_type == "ext":
            examples = _create_ext_examples(raw_examples, negative_ratio,
                                            is_shuffle)
        else:
            examples = _create_cls_examples(raw_examples, prompt_prefix,
                                            options, is_shuffle)
        _save_examples(save_dir, "train.txt", examples)
    else:
        if is_shuffle:
            indexes = np.random.permutation(len(raw_examples))
            raw_examples = [raw_examples[i] for i in indexes]

        i1, i2, _ = splits
        p1 = int(len(raw_examples) * i1)
        p2 = int(len(raw_examples) * (i1 + i2))

        if task_type == "ext":
            train_examples = _create_ext_examples(
                raw_examples[:p1], negative_ratio, is_shuffle)
            dev_examples = _create_ext_examples(raw_examples[p1:p2])
            test_examples = _create_ext_examples(raw_examples[p2:])
        else:
            train_examples = _create_cls_examples(
                raw_examples[:p1], prompt_prefix, options)
            dev_examples = _create_cls_examples(
                raw_examples[p1:p2], prompt_prefix, options)
            test_examples = _create_cls_examples(
                raw_examples[p2:], prompt_prefix, options)

        _save_examples(save_dir, "train.txt", train_examples)
        _save_examples(save_dir, "dev.txt", dev_examples)
        _save_examples(save_dir, "test.txt", test_examples)

    print('Finished! It takes %.2f seconds' % (time.time() - tic_time))


if __name__ == "__main__": 
    do_convert()