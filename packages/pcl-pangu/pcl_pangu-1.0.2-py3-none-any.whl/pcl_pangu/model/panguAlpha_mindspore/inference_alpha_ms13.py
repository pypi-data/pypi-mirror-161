# Copyright 2021 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""
PanGu predict run
"""
import os

import numpy as np

import mindspore.common.dtype as mstype
import mindspore.communication.management as D
from mindspore import context, Tensor
from mindspore import export
from mindspore.context import ParallelMode
from mindspore.parallel import set_algo_parameters
from mindspore.parallel._cost_model_context import _set_multi_subgraphs
from mindspore.train.model import Model
## from mindspore.train.serialization import load_distributed_checkpoint
from src.serialization import load_distributed_checkpoint
from src.pangu_alpha import PanguAlpha, EvalNet
from src.pangu_alpha_config import PANGUALPHAConfig, set_parse
from src.utils_pangu import get_args

import time
import moxing as mox
from src.utils_pangu import download_data, ckpt_copy_tar_new, get_ckpt_file_list

import mindspore.nn as nn
from mindspore.nn.wrap.cell_wrapper import PipelineCell, _VirtualDatasetCell


def load_model(args_opt):
    r"""
     The main function for load model
    """
    # Set execution mode
    context.set_context(save_graphs=False,
                        mode=context.GRAPH_MODE,
                        device_target=args_opt.device_target)
    context.set_context(variable_memory_max_size="30GB")
    # Set parallel context
    if args_opt.distribute == "true":
        D.init()
        device_num = D.get_group_size()
        rank = D.get_rank()
        print("rank_id is {}, device_num is {}".format(rank, device_num))

        local_strategy_ckpt_path = args_opt.strategy_load_ckpt_path

        # local_strategy_ckpt_path = "/cache/ckpt_strategy.ckpt"
        # if rank % 8 == 0:
        #     os.system('ulimit -s 102400')
        #     mox.file.copy(src_url=args_opt.strategy_load_ckpt_path, dst_url=local_strategy_ckpt_path)
        #     steps_name = args_opt.load_ckpt_obs_path.split('/')[-1].split('-')[-1]
        #     print("steps_name", steps_name)
        #     name_in = args_opt.load_obs_ckptname
        #     ckpt_copy_tar_new(args_opt.load_ckpt_obs_path + name_in, target_path=args_opt.load_ckpt_local_path)
        #     mox.file.copy(f'{args_opt.load_ckpt_obs_path}/{name_in}_word_embedding.npy',
        #                   f'{args_opt.load_ckpt_local_path}/word_embedding.npy')
        #     mox.file.copy(f'{args_opt.load_ckpt_obs_path}/{name_in}_position_embedding.npy',
        #                   f'{args_opt.load_ckpt_local_path}/position_embedding.npy')
        #     mox.file.copy(f'{args_opt.load_ckpt_obs_path}/{name_in}_top_query_embedding.npy',
        #                   f'{args_opt.load_ckpt_local_path}/top_query_embedding.npy')
        #     print("setting env success.")
        #     # 下载模型文件结束后，写一个文件来表示下载成功
        #     f = open("/tmp/download_ckpt.txt", 'w')
        #     f.close()
        # # 此处用于阻塞其他进程，直到刷包以及下载数据集完成为止
        # while not os.path.exists("/tmp/download_ckpt.txt"):
        #     time.sleep(1)
        # print("\n\n************Checkpoint download succeed!*************\n\n", flush=True)
        if rank % 8 == 0:
            print(os.listdir(args_opt.load_ckpt_local_path), flush=True)

        context.reset_auto_parallel_context()
        context.set_auto_parallel_context(
            parallel_mode=ParallelMode.SEMI_AUTO_PARALLEL,
            gradients_mean=False,
            full_batch=True,
            loss_repeated_mean=True,
            enable_parallel_optimizer=False,
            strategy_ckpt_load_file=local_strategy_ckpt_path,
            pipeline_stages=args_opt.stage_num)
        set_algo_parameters(elementwise_op_strategy_follow=True)
        _set_multi_subgraphs()

    else:
        rank = 0
        device_num = 1
        context.reset_auto_parallel_context()
        context.set_auto_parallel_context(
            strategy_ckpt_load_file=local_strategy_ckpt_path)

    use_past = (args_opt.use_past == "true")
    print('local_rank:{}, start to run...'.format(rank), flush=True)
    if args_opt.export:
        use_past = True
    # Set model property
    model_parallel_num = args_opt.op_level_model_parallel_num
    data_parallel_num = int(device_num / model_parallel_num)
    per_batch_size = args_opt.per_batch_size
    batch_size = per_batch_size * data_parallel_num
    # Now only support single batch_size for predict
    if args_opt.run_type == "predict":
        batch_size = 1
    config = PANGUALPHAConfig(
        data_parallel_num=data_parallel_num,
        model_parallel_num=model_parallel_num,
        batch_size=batch_size,
        seq_length=args_opt.seq_length,
        vocab_size=args_opt.vocab_size,
        embedding_size=args_opt.embedding_size,
        num_layers=args_opt.num_layers,
        num_heads=args_opt.num_heads,
        expand_ratio=4,
        post_layernorm_residual=False,
        dropout_rate=0.0,
        compute_dtype=mstype.float16,
        use_past=use_past,
        stage_num=args_opt.stage_num,
        micro_size=args_opt.micro_size,
        eod_reset=False,
        word_emb_dp=True,
        load_ckpt_path=args_opt.load_ckpt_local_path,
        param_init_type=mstype.float32 if args_opt.param_init_type == 'fp32' else mstype.float16)
    print("===config is: ", config, flush=True)
    print("=====args_opt is: ", args_opt, flush=True)

    ckpt_name = args_opt.load_ckpt_name
    # Define network
    pangu_alpha = PanguAlpha(config)
    ################################
    from src.pangu_alpha import PanguAlphaWithLoss_eval_nli, CrossEntropyLoss, PanguAlphaWithLoss_eval
    loss = CrossEntropyLoss(config)
    # eval_net = PanguAlphaWithLoss_eval_nli(config, pangu_alpha, loss, eos_token=128297)
    eval_net = PanguAlphaWithLoss_eval(config, pangu_alpha, loss, eos_token=128297)
    eval_net = _VirtualDatasetCell(eval_net)
    eval_net.set_train(False)
    ################################
    # eval_net = EvalNet(pangu_alpha)
    # eval_net.set_train(False)
    model_predict = Model(eval_net)
    # Compile network and obtain tensor layout for loading ckpt
    inputs_np = Tensor(np.ones(shape=(config.batch_size, config.seq_length)), mstype.int32)
    current_index = Tensor(np.array([0]), mstype.int32)

    if args_opt.distribute == "false":
        predict_layout = None
    elif config.use_past:
        fake_input = Tensor(np.ones(shape=(1, config.seq_length + 1)), mstype.int32)
        mask_ids = Tensor(np.ones(shape=(1, config.seq_length)), mstype.float32)
        predict_layout = model_predict.infer_predict_layout(fake_input, mask_ids)

    #         batch_valid_length = Tensor(np.array([0]), mstype.int32)
    #         init_true = Tensor([True], mstype.bool_)
    #         inputs_np_1 = Tensor(np.ones(shape=(config.batch_size, 1)), mstype.int32)
    #         model_predict.predict_network.add_flags_recursive(is_first_iteration=True)
    #         predict_layout = model_predict.infer_predict_layout(inputs_np, current_index, init_true, batch_valid_length)
    #         model_predict.predict_network.add_flags_recursive(is_first_iteration=False)
    #         _ = model_predict.infer_predict_layout(inputs_np_1, current_index, init_true, batch_valid_length)
    else:
        predict_layout = model_predict.infer_predict_layout(inputs_np, current_index)
    ##------------------------------------------------------------------------------------------------------
    print("======start load_distributed checkpoint", flush=True)
    if args_opt.num_layers == 24:
        ckpt_file_list = get_ckpt_file_list(args_opt.load_ckpt_local_path, device_num=128)
    else:
        ckpt_file_list = get_ckpt_file_list(args_opt.load_ckpt_local_path, device_num=512)

    # For 2.6B and 13B models, the number of ckpt files is 512.
    ## ckpt_name = 'filerted'
    ## ckpt_file_list = [os.path.join(args_opt.load_ckpt_path, f"{ckpt_name}_{ckpt_rank}.ckpt") for ckpt_rank in
    ##                   range(0, 512)]
    print(ckpt_file_list)
    print(f"Loading from path {ckpt_file_list[0]}", flush=True)
    # Load checkpoint files
    # print(ckpt_file_list)
    # print(predict_layout)
    load_distributed_checkpoint(eval_net, ckpt_file_list, predict_strategy=predict_layout)
    print("================load param ok=================", flush=True)
    ##-------------------------------------------------------------------------------------------------------
    return model_predict, config


def export_mindir(model_predict, config):
    """Export mindir model"""
    inputs_np = Tensor(np.ones(shape=(config.batch_size, config.seq_length)), mstype.int32)
    current_index = Tensor(np.array([0]), mstype.int32)

    batch_valid_length = Tensor(np.array([0]), mstype.int32)
    init_true = Tensor([True], mstype.bool_)
    inputs_np_1 = Tensor(np.ones(shape=(config.batch_size, 1)), mstype.int32)

    model_predict.predict_network.add_flags_recursive(is_first_iteration=True)
    export(model_predict.predict_network, inputs_np, current_index,
           init_true, batch_valid_length, file_name='pangu_alpha_1024', file_format='MINDIR')
    model_predict.predict_network.add_flags_recursive(is_first_iteration=False)
    export(model_predict.predict_network, inputs_np_1, current_index,
           init_true, batch_valid_length, file_name='pangu_alpha_1', file_format='MINDIR')
    print("Export finished and now exit.")


def run_predict(model_predict, config, args_opt):
    """run predict"""
    from src.tokenization_jieba import JIEBATokenizer
    from src.generate import generate, generate_increment
    # Define tokenizer
    tokenizer = JIEBATokenizer(os.path.join(args_opt.tokenizer_path, 'vocab10.vocab'),
                               os.path.join(args_opt.tokenizer_path, 'vocab10.model'))

    samples = args_opt.input
    input_file = args_opt.input_file
    output_file = args_opt.output_file

    if input_file is None:
        # Tokenize input sentence to ids
        for input_sentence in samples:
            print('> Input is:\n')
            tokenized_token = tokenizer.tokenize(input_sentence)
            start_sentence = tokenizer.convert_tokens_to_ids(tokenized_token)
            input_ids = np.array(start_sentence).reshape(1, -1)
            # Call inference
            generate_func = generate_increment if config.use_past else generate
            output_ids = generate_func(model_predict, input_ids, args_opt)
            # Decode output ids to sentence
            output_samples = tokenizer.convert_ids_to_tokens(output_ids.tolist())
            print('> Output is:\n', output_samples, flush=True)

def run_predict_mpg(model_predict, config, args_opt):
    """run predict"""
    # from src.tokenization_jieba import JIEBATokenizer
    from src.generate import generate, generate_increment
    from pcl_pangu.tokenizer.spm_13w.tokenizer import SpmTokenizer, langs_ID, translate_ID
    tokenizer = SpmTokenizer(args_opt.tokenizer_path)

    samples = args_opt.input
    input_file = args_opt.input_file
    output_file = args_opt.output_file

    if input_file is None:
        # Tokenize input sentence to ids
        for input_sentence in samples:
            print('> Input is:\n')
            tokenized_token = tokenizer.tokenize(input_sentence)
            start_sentence = tokenizer.convert_tokens_to_ids(tokenized_token)
            start_sentence = [langs_ID[args_opt.src_language], langs_ID[args_opt.src_language], langs_ID[args_opt.src_language]] +\
                             start_sentence + \
                             [translate_ID, translate_ID, translate_ID] + \
                             [langs_ID[args_opt.tag_language], langs_ID[args_opt.tag_language], langs_ID[args_opt.tag_language]]
            input_ids = np.array(start_sentence).reshape(1, -1)
            # Call inference
            generate_func = generate_increment if config.use_past else generate
            output_ids = generate_func(model_predict, input_ids, args_opt)
            # Decode output ids to sentence
            output_samples = tokenizer.convert_ids_to_tokens(output_ids.tolist())
            print('> Output is:\n', output_samples, flush=True)

def main(opt):
    """Main process for predict or export model"""

    model_predict, config = load_model(opt)
    if opt.export:
        export_mindir(model_predict, config)
    else:
        if opt.src_language == "":
            run_predict(model_predict, config, opt)
        else:
            run_predict_mpg(model_predict, config, opt)

def setup_args(args_opt, model_config_dict):
    args_opt.op_level_model_parallel_num = model_config_dict.get('model_parallel_size')
    args_opt.per_batch_size = model_config_dict.get('batch_size')
    args_opt.seq_length = model_config_dict.get('seq_length')
    args_opt.embedding_size = model_config_dict.get('hidden_size')
    args_opt.num_layers = model_config_dict.get('num_layers') + 1
    args_opt.num_heads = model_config_dict.get('num_attention_heads')
    args_opt.start_lr = model_config_dict.get('start_lr')
    args_opt.end_lr = model_config_dict.get('end_lr')
    args_opt.decay_steps = model_config_dict.get('lr_decay_iters')
    args_opt.epoch_size = model_config_dict.get('train_epoch_size')
    args_opt.strategy_load_ckpt_path = model_config_dict.get('strategy_load_ckpt_path')
    args_opt.load_ckpt_local_path = model_config_dict.get('load')
    args_opt.save_checkpoint_bucket_dir = model_config_dict.get('save')
    args_opt.data_url = model_config_dict.get('data_path')
    args_opt.top_k = model_config_dict.get('top_k')
    args_opt.top_p = model_config_dict.get('top_p')
    args_opt.input = model_config_dict.get('input')
    args_opt.input_file = model_config_dict.get('input_file')
    args_opt.output_file = model_config_dict.get('output_file')

    return args_opt

def extend_setup_args_for_mPangu(args_opt, model_config_dict):
    args_opt.vocab_size = model_config_dict.get('vocab_size')
    args_opt.tokenizer_path = model_config_dict.get('vocab_file')
    args_opt.src_language = model_config_dict.get('src_language')
    args_opt.tag_language = model_config_dict.get('tag_language')

    return args_opt


opt = get_args(True)
set_parse(opt)