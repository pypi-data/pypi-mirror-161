#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Date: 2022/7/20
# @Author: 2022 PCL
import os
import sys
from loguru import logger
from ..launcher_torch import launch

from pcl_pangu.context import check_context
from .config_mPangu import DISTRUBUTED_CONFIG, model_config_gpu, model_config_npu


def train(config):
    print('---------------------------- train config ----------------------------')
    print("> Base Model: [alpha]")
    print("> Model Size: [{}]".format(config.model))
    print("> data_path: {}".format(config.data_path))
    print("> global batch_size: {}".format(config.batch_size))
    print("> save to path: {}".format(config.save))
    print('--------------------------- end of config ----------------------------')

    if check_context()=='pytorch':
        assert isinstance(config, model_config_gpu)
        script_args = config._get_training_script_args()
        py_script = '/panguAlpha_pytorch/pretrain_gpt2.py'
        run_pt(script_args, py_script)
    elif check_context()=='mindspore':
        assert isinstance(config, model_config_npu)
        config_dict = config._cover_modelarts_training_args()
        run_ms_train(config_dict)



def fine_tune(config):
    print('-------------------------- finetune config ---------------------------')
    print("> Base Model: [alpha]")
    print("> Model Size: [{}]".format(config.model))
    print("> data_path: {}".format(config.data_path))
    print("> global batch_size: {}".format(config.batch_size))
    print("> save to path: {}".format(config.save))
    print('--------------------------- end of config ----------------------------')

    if check_context()=='pytorch':
        from .config_mPangu import DEFAULT_CONFIG
        DEFAULT_CONFIG['finetune'] = True
        script_args = config._get_training_script_args()
        py_script = '/panguAlpha_pytorch/pretrain_gpt2.py'
        run_pt(script_args, py_script)
    elif check_context()=='mindspore':
        assert isinstance(config, model_config_npu)
        config_dict = config._cover_modelarts_training_args()
        run_ms_train(config_dict)


def inference(config,top_k=1,top_p=0.9,input=None,input_file=None,output_file=None):
    print('--------------------------- inference config --------------------------')
    print("> Base Model: [alpha]")
    print("> Model Size: [{}]".format(config.model))
    print("> data_path: {}".format(config.data_path))
    print("> global batch_size: {}".format(config.batch_size))
    print("> save to path: {}".format(config.save))
    print('---------------------------- end of config ----------------------------')

    if check_context()=='pytorch':
        from .config_mPangu import DEFAULT_CONFIG
        DEFAULT_CONFIG['finetune'] = True
        config.batch_size = 1
        script_args = config._get_training_script_args()
        py_script = '/panguAlpha_pytorch/tools/generate_samples_Pangu.py'
        script_args.append('--top-k={}'.format(top_k))
        script_args.append('--top-p={}'.format(top_p))
        if input is not None:
            script_args.append('--sample-input={}'.format(input.encode('utf-8').hex()))
        if input_file is not None:
            script_args.append('--sample-input-file={}'.format(input_file))
        if output_file is not None:
            script_args.append('--sample-output-file={}'.format(output_file))
        run_pt(script_args, py_script)

    elif check_context()=='mindspore':
        assert isinstance(config, model_config_npu)
        config_dict = config._cover_modelarts_training_args()
        config_dict['top_k'] = top_k
        config_dict['top_p'] = top_p
        config_dict['input'] = input
        config_dict['input_file'] = input_file
        config_dict['output_file'] = output_file

def run_pt(script_args, py_script, **kwargs):
    current_dir = os.path.dirname(os.path.dirname(__file__))
    sys.path.append(current_dir+'/panguAlpha_pytorch')
    py_script = current_dir + py_script
    logger.info("> Running {} with args: {}".format(py_script, script_args))
    launch(training_script=py_script,
           training_script_args=script_args,
           **DISTRUBUTED_CONFIG,
           **kwargs)


def run_ms_train(config_dict):
    current_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
    sys.path.append(current_dir + '/panguAlpha_mindspore')
    from train_alpha_ms13 import opt, setup_args, main
    new_opt = setup_args(opt, config_dict)
    main(new_opt)

def run_ms_inference(config_dict):
    current_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
    sys.path.append(current_dir + '/panguAlpha_mindspore')
    from inference_alpha_ms13 import opt, setup_args, extend_setup_args_for_mPangu, main
    new_opt = setup_args(opt, config_dict)
    new_opt = extend_setup_args_for_mPangu(new_opt, config_dict)
    main(new_opt)

if __name__ == '__main__':
    config = model_config_gpu()
    run_pt(config)
