# Copyright 2022 PCL, Huawei Technologies Co., Ltd
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
PanguAlpha train script
"""

import os
import math
import time
from pathlib2 import Path

from mindspore import context
from mindspore.train.model import Model
import mindspore.communication.management as D
from mindspore.context import ParallelMode
import mindspore.nn as nn
from mindspore.train.callback import TimeMonitor, Callback
from mindspore.nn.wrap.loss_scale import DynamicLossScaleUpdateCell
import mindspore.common.dtype as mstype
from mindspore.parallel import set_algo_parameters
from mindspore.parallel._cost_model_context import _set_multi_subgraphs
from mindspore.nn.wrap.cell_wrapper import PipelineCell, _VirtualDatasetCell
from mindspore.train.callback import ModelCheckpoint, CheckpointConfig
from mindspore.train.serialization import load_checkpoint, load_param_into_net

from src.dataset import create_dataset
from src.pangu_alpha import PanguAlpha, PanguAlphaWithLoss, CrossEntropyLoss
from src.pangu_alpha_wrapcell import PanguAlphaTrainOneStepWithLossScaleCell
from src.pangu_alpha_config import PANGUALPHAConfig, set_parse
from src.utils_pangu import LearningRate, get_args, FP32StateAdamWeightDecay
from src.utils_pangu import download_data, ckpt_copy_tar_new, get_ckpt_file_list
from src.utils_pangu import StrategySaveCallback, CheckpointSaveCallback

import moxing as mox


project_root = os.path.abspath(
    os.path.dirname(os.path.realpath(__file__)) + os.path.sep + "..")
print('project_root:', project_root)


class LossCallBack(Callback):
    """
    Monitor the loss in training.
    If the loss in NAN or INF terminating training.
    """

    def __init__(self, dataset_size=-1, local_rank=0, has_trained_epoch=0, has_trained_step=0, micro_size=1):
        super(LossCallBack, self).__init__()
        self._dataset_size = dataset_size
        self.local_rank = local_rank
        self.has_trained_epoch = has_trained_epoch
        self.has_trained_step = has_trained_step
        self.micro_size = micro_size
        print("load has trained epoch :{} and step: {}".format(has_trained_epoch, has_trained_step), flush=True)

    def step_end(self, run_context):
        """
        Print loss after each step
        """
        cb_params = run_context.original_args()
        if self._dataset_size > 0 and self.local_rank % 8 == 0:
            percent, epoch_num = math.modf(cb_params.cur_step_num /
                                           self._dataset_size)
            if percent == 0:
                epoch_num -= 1
            date = time.asctime(time.localtime(time.time()))
            loss_value = cb_params.net_outputs[0].asnumpy() / self.micro_size
            D.init()
            rank = D.get_rank()
            log_local_tmp = "/cache/train_log_node.txt"
            if rank%8 == 0:
                lines = "time: {} local_rank: {}, epoch: {}, step: {}, loss is {}, overflow is {}, scale is {}, lr is {}".format(date, 
                             int(self.local_rank), 
                             int(epoch_num) + int(self.has_trained_epoch),
                             cb_params.cur_step_num + int(self.has_trained_step), 
                             loss_value,
                             cb_params.net_outputs[1].asnumpy(), 
                             cb_params.net_outputs[2].asnumpy(),
                             cb_params.net_outputs[3].asnumpy())
                print(lines)


def add_checkpoint_callback_policy(args_param, callback, rank_id):
    r"""
    Add checkpoint policy to callback.
    """
    if args_param.save_checkpoint:
        if not os.path.exists(args_param.save_checkpoint_path):
            os.makedirs(args_param.save_checkpoint_path, exist_ok=True)
        if not mox.file.exists(args_param.save_checkpoint_bucket_dir):
            mox.file.make_dirs(args_param.save_checkpoint_bucket_dir) 
        # checkpoint store epoch_num and step_num info
        ckpt_append_info = [{"epoch_num": args_param.has_trained_epoches, "step_num": args_param.has_trained_steps}]
        ckpt_config = CheckpointConfig(save_checkpoint_steps=args_param.save_checkpoint_steps,
                                       keep_checkpoint_max=1,
                                       integrated_save=False,
                                       append_info=ckpt_append_info
                                       )
        save_dir_rank = os.path.join(args_param.save_checkpoint_path, f"rank_{rank_id}")
        save_ckptfile_name = args_param.ckpt_name_prefix + '_' + str(rank_id)
        if not os.path.exists(save_dir_rank):
            os.makedirs(save_dir_rank, exist_ok=True)
        ckpoint_cb = ModelCheckpoint(prefix=args_param.ckpt_name_prefix + '_' + str(rank_id),
                                     directory=save_dir_rank,
                                     config=ckpt_config)
    
        ckpt_save_obs_cb = CheckpointSaveCallback(local_ckpt_dir=save_dir_rank, 
                                              local_rank=rank_id, 
                                              has_trained_epoch=args_param.has_trained_epoches,
                                              has_trained_step=args_param.has_trained_steps, 
                                              bucket=args_param.save_checkpoint_bucket_dir,
                                              syn_obs_steps=args_param.save_checkpoint_steps)
        callback.append(ckpoint_cb)
        callback.append(ckpt_save_obs_cb)
        
    if rank_id == 0:
        sub_dir = args_param.save_checkpoint_bucket_dir.split('/')[-1]
        callback.append(StrategySaveCallback(strategy_path='/cache/strategy.ckpt', 
                                            local_rank=0, 
                                            has_trained_epoch=args_param.has_trained_epoches,
                                            has_trained_step=args_param.has_trained_steps, 
                                            bucket=args_param.save_strategy_bucket_dir))
                                            ## bucket='obs://research-my/taoht-13b/strategy_ckpt/' + sub_dir))


def load_train_net(args_opt):
    r"""
    The main training process.
    """
    # Set hccl connect time
    os.environ['HCCL_CONNECT_TIMEOUT'] = "7200"
    
    # Set execution mode
    context.set_context(mode=context.GRAPH_MODE, device_target=args_opt.device_target)
    context.set_context(variable_memory_max_size="30GB")
    print(args_opt)
    # Set parallel context
    if args_opt.distribute == "true":
        D.init()
        device_num = D.get_group_size()
        rank = D.get_rank()
        print("rank_id is {}, device_num is {}".format(rank, device_num))

        context.reset_auto_parallel_context()
        
        local_strategy_ckpt_path="/cache/ckpt_strategy.ckpt"
        if args_opt.pre_trained:
                os.system('ulimit -s 102400')
                mox.file.copy(src_url=args_opt.strategy_load_ckpt_path, dst_url=local_strategy_ckpt_path)
        
        if args_opt.pre_trained:
            if args_opt.device_num > 64:
                context.set_auto_parallel_context(
                    parallel_mode=ParallelMode.SEMI_AUTO_PARALLEL, 
                    gradients_mean=False,
                    full_batch=bool(args_opt.full_batch), 
                    strategy_ckpt_load_file=local_strategy_ckpt_path,
                    enable_parallel_optimizer=bool(args_opt.optimizer_shard), 
                    optimizer_weight_shard_size=64,
                    strategy_ckpt_save_file='/cache/strategy.ckpt')
#                     optimizer_weight_shard_aggregated_save=True,
                    
            else:
                context.set_auto_parallel_context(
                    parallel_mode=ParallelMode.SEMI_AUTO_PARALLEL, 
                    gradients_mean=False,
                    full_batch=bool(args_opt.full_batch), 
                    strategy_ckpt_load_file=local_strategy_ckpt_path,
                    enable_parallel_optimizer=bool(args_opt.optimizer_shard), 
                    optimizer_weight_shard_aggregated_save=True,
                    strategy_ckpt_save_file='/cache/strategy.ckpt')
        else:
            if args_opt.device_num > 64:
                context.set_auto_parallel_context(
                    parallel_mode=ParallelMode.SEMI_AUTO_PARALLEL, 
                    gradients_mean=False,
                    full_batch=bool(args_opt.full_batch),
                    enable_parallel_optimizer=bool(args_opt.optimizer_shard), 
                    optimizer_weight_shard_size=64,
                    strategy_ckpt_save_file='/cache/strategy.ckpt')
                    ## optimizer_weight_shard_aggregated_save=True,
            else:
                context.set_auto_parallel_context(
                    parallel_mode=ParallelMode.SEMI_AUTO_PARALLEL, 
                    gradients_mean=False,
                    full_batch=bool(args_opt.full_batch), 
                    enable_parallel_optimizer=bool(args_opt.optimizer_shard),
                    optimizer_weight_shard_aggregated_save=True,
                    strategy_ckpt_save_file='/cache/strategy.ckpt')
        
        set_algo_parameters(elementwise_op_strategy_follow=True)
        _set_multi_subgraphs()
    else:
        rank = 0
        device_num = 1
    context.set_context(save_graphs=False, save_graphs_path="./graphs_of_device_id_" + str(rank))
    ###################################################
    ## context.set_context(enable_graph_kernel=True)
    ###################################################
    # copy data from the cloud to the /cache/Data
    cache_url = "/cache/Data/"
    if args_opt.offline:
        cache_url = args_opt.data_url
    else:
        download_data(src_data_url=args_opt.data_url, tgt_data_path=cache_url, rank=rank)

    # Set model property
    model_parallel_num = args_opt.op_level_model_parallel_num
    assert device_num >= model_parallel_num, '> device_num must bigger than model_parallel_num'
    data_parallel_num = int(device_num / model_parallel_num)
    batch_size = args_opt.per_batch_size #* data_parallel_num
    assert batch_size >= data_parallel_num, '> global batch_size must bigger than data_parallel_num'

    config = PANGUALPHAConfig(
        data_parallel_num=data_parallel_num, 
        model_parallel_num=model_parallel_num, 
        batch_size=batch_size,
        seq_length=args_opt.seq_length, 
        vocab_size=args_opt.vocab_size, 
        embedding_size=args_opt.embedding_size,
        num_layers=args_opt.num_layers, 
        num_heads=args_opt.num_heads, 
        expand_ratio=4, dropout_rate=0.1,
        compute_dtype=mstype.float16, 
        stage_num=args_opt.stage_num, 
        micro_size=args_opt.micro_size,
        eod_reset=bool(args_opt.eod_reset), 
        load_ckpt_path=None, ##args_opt.load_ckpt_local_path,## incremental_training ckpt load，None
        param_init_type=mstype.float32 if args_opt.param_init_type == 'fp32' else mstype.float16,
        word_emb_dp=bool(args_opt.word_emb_dp))
    print("===config is: ", config, flush=True)

    # Define network
    pangu_alpha = PanguAlpha(config)
    loss = CrossEntropyLoss(config)
    pangu_alpha_with_loss = PanguAlphaWithLoss(config, pangu_alpha, loss)
    pangu_alpha_with_loss = _VirtualDatasetCell(pangu_alpha_with_loss)
    
    
    # Warm-up and cosine decay learning rate
    lr = LearningRate(learning_rate=args_opt.start_lr, end_learning_rate=args_opt.end_lr,
                      warmup_steps=args_opt.warmup_step, decay_steps=args_opt.decay_steps)

    # Set weight decay coefficient, zero for bias and layernorm, 1e-1 for rest
    decay_filter = lambda x: 'layernorm' not in x.name.lower() and "bias" not in x.name.lower()
    params = pangu_alpha.trainable_params()
    decay_params = list(filter(decay_filter, params))
    other_params = list(filter(lambda x: not decay_filter(x), params))
    group_params = [{
        'params': decay_params,
        'weight_decay': 1e-1
    }, {
        'params': other_params,
        'weight_decay': 0.0
    }, {
        'order_params': params
    }]
    if args_opt.optimizer == "lamb":
        optimizer = nn.Lamb(group_params, learning_rate=lr)
    else:
        optimizer = FP32StateAdamWeightDecay(group_params, learning_rate=lr, eps=1e-8, beta1=0.9, beta2=0.95)## 0.95
    # Initial scaling sens
    loss_scale_value = math.pow(2, 16)
    
    #################################################################
    callback_size = args_opt.sink_size
    if args_opt.distribute == "true":
        D.init()
        device_num = D.get_group_size()
        rank = D.get_rank()
    if args_opt.pre_trained:
        callback = [
            TimeMonitor(callback_size),
            LossCallBack(callback_size, rank, args_opt.has_trained_epoches, args_opt.has_trained_steps)
        ]
    else:
        callback = [
        TimeMonitor(callback_size), LossCallBack(callback_size, rank, 0, 0)]
    ##################################################################

    update_cell = DynamicLossScaleUpdateCell(loss_scale_value=loss_scale_value, scale_factor=2, scale_window=100)
    pangu_alpha_with_grads = PanguAlphaTrainOneStepWithLossScaleCell(
        pangu_alpha_with_loss, 
        optimizer=optimizer, 
        scale_update_cell=update_cell, 
        enable_global_norm=True,
        config=config)
    model = Model(pangu_alpha_with_grads)

    if not mox.file.exists(args_opt.save_checkpoint_bucket_dir):
        mox.file.make_dirs(args_opt.save_checkpoint_bucket_dir) 
    
    epoch_num = args_opt.epoch_size

    # Dataset loading mindrecord files
    ds = create_dataset(config.batch_size, 
                        data_path=cache_url,
                        data_start_index=0, #args_opt.data_start_index, 
                        eod_reset=config.eod_reset, 
                        full_batch=bool(args_opt.full_batch),
                        eod_id=args_opt.eod_id, 
                        device_num=device_num, 
                        rank=rank,
                        column_name=args_opt.data_column_name, 
                        epoch=epoch_num)
    
    return pangu_alpha, args_opt, model, ds, callback, config


def restore_filtered_ckpt_from_obs_incremental_training(args_opt, model):
    r"""
    Load checkpoint process.
    """
    import moxing as mox
    
    if args_opt.incremental_training:
        local_strategy_ckpt_path="/cache/ckpt_strategy.ckpt"
        if rank % 8 == 0:
            print("Incremental training", flush=True)
            os.system('ulimit -s 102400')
            mox.file.copy(src_url=args_opt.strategy_load_ckpt_path, dst_url=local_strategy_ckpt_path)
            ckpt_copy_tar_new(args_opt.load_filter_ckpt_bucket_dir, target_path=args_opt.load_ckpt_local_path)
            mox.file.copy(f'{args_opt.load_ckpt_obs_path}_word_embedding.npy', f'{args_opt.load_ckpt_local_path}/word_embedding.npy')
            mox.file.copy(f'{args_opt.load_ckpt_obs_path}_position_embedding.npy', f'{args_opt.load_ckpt_local_path}/position_embedding.npy')
            mox.file.copy(f'{args_opt.load_ckpt_obs_path}_top_query_embedding.npy', f'{args_opt.load_ckpt_local_path}/top_query_embedding.npy')
            print("setting env success.")
            # 下载模型文件结束后，写一个文件来表示下载成功
            f = open("/tmp/download_ckpt.txt", 'w')
            f.close()
    if args_opt.incremental_training:
        # 此处用于阻塞其他进程，直到刷包以及下载数据集完成为止
        while not os.path.exists("/tmp/download_ckpt.txt"):
            time.sleep(1)
        print("\n\n************Checkpoint download succeed!*************\n\n", flush=True)
        if rank % 8 == 0:
            print(os.listdir(args_opt.load_ckpt_local_path), flush=True)
    
    if args_opt.incremental_training:
        from mindspore.train.serialization import load_distributed_checkpoint
        ckpt_file_list = get_ckpt_file_list(args_opt.load_ckpt_local_path, device_num=128)
        print("Start to load distributed checkpoint", flush=True)
        print(f"Loading from path {ckpt_file_list[0]}", flush=True)
        load_distributed_checkpoint(model.train_network, ckpt_file_list)


def restore_pretrain_integrated_ckpt_from_obs(args_opt, model):
    import moxing as mox
    from pathlib2 import Path
    
    D.init()
    rank_id = D.get_rank()
    
    if args_opt.incremental_training:
        local_integrated_ckpt_path="/cache/ckpt_integrated_tmp.ckpt"
        if rank_id % 8 == 0:
            print("Download checkpoint ...", flush=True)
            os.system('ulimit -s 102400')
            mox.file.copy(src_url="obs://research-my/Cloud_compute/ckpt/pretrain_ckpt/Pangu-alpha_2.6B.ckpt", dst_url=local_integrated_ckpt_path)
            # 下载模型文件结束后，写一个文件来表示下载成功
            f = open("/tmp/download_ckpt.txt", 'w')
            f.close()
            
    if args_opt.incremental_training:
        # 此处用于阻塞其他进程，直到刷包以及下载数据集完成为止
        while not os.path.exists("/tmp/download_ckpt.txt"):
            time.sleep(1)
        print("\n\n************Checkpoint download succeed!*************\n\n", flush=True)
    
    if args_opt.incremental_training:
        parameters = load_checkpoint(local_integrated_ckpt_path)
        load_param_into_net(model.train_network, parameters)
       

def main(opt):
    os.environ['HCCL_CONNECT_TIMEOUT'] = "7200"
    net, args_opt, model, ds, callback, config = load_train_net(opt)
    
    D.init()
    device_num = D.get_group_size()
    rank_id = D.get_rank()

    model_parallel_num = args_opt.op_level_model_parallel_num
    assert device_num >= model_parallel_num, '> device_num must bigger than model_parallel_num'
    data_parallel_num = int(device_num / model_parallel_num)
    batch_size = args_opt.per_batch_size  # * data_parallel_num
    assert batch_size >= data_parallel_num, '> global batch_size must bigger than data_parallel_num'


    step_per_epoch = ds.get_dataset_size()
    callback_size = args_opt.sink_size
    actual_epoch_num = int(step_per_epoch / callback_size)
    
    print("\n=====dataset size: ", ds.get_dataset_size(), flush=True)
    print("=====batchsize: ", batch_size, flush=True)
    print("=====actual_epoch_num: ", actual_epoch_num, flush=True)
    print(f"=====mp: {model_parallel_num}, dp: {data_parallel_num}\n")
    #################################################################
    
    add_checkpoint_callback_policy(args_opt, callback, rank_id)
    
    # 变策略迁移学习
    if args_opt.incremental_training:
        restore_pretrain_integrated_ckpt_from_obs(args_opt, model)
    # 初始化，从头学习
    else:
        model._init(train_dataset=ds, sink_size=2)
    model.train(actual_epoch_num, ds, callbacks=callback, sink_size=callback_size, dataset_sink_mode=True)
            

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
    args_opt.save_checkpoint_bucket_dir = model_config_dict.get('save')
    args_opt.data_url = model_config_dict.get('data_path')
    args_opt.vocab_size = model_config_dict.get('vocab_size')


    return args_opt


opt = get_args()


# set_parse(opt)
# obs_upload_dir = 'ckpt_pd_cmrc'
# main(opt, obs_upload_dir)
