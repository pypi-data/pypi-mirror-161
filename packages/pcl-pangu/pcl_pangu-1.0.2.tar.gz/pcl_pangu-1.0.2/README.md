<div align=center>
<img src="./docs/pangu-logo.png" width="238" height="245"/><br/>
</div>

# pcl_pangu: 鹏程·盘古SDK Beta版

## 简介

欢迎您使用鹏程·盘古SDK Beta版——pcl_pangu Beta！，如果您使用过程中有任何问题请加入鹏程·盘古技术交流群进行交流[[加入](#微信交流群)]，或者在<任务>中提issue。

pcl_pangu项目的目标是将 `鹏程·盘古`[[项目主页](https://git.openi.org.cn/PCL-Platform.Intelligence/PanGu-Alpha)]开源模型、以及基于该模型的一系列任务拓展与持续学习得到的模型从语料数据预处理到模型训练推理部署整个流水线封装成开发工具包SDK。其目标与特点在于：

- 向开发者提供简单易用的 鹏程·盘古应用拓展API，包括数据预处理、模型预训练、推理、微调、模型转换、模型压缩等功能。您可以快速体验鹏程·盘古大模型，并且可以轻松的开发自己的模型；
- 向开发者提供基于鹏程·盘古大模型的应用拓展案例，如：鹏程.盘古增强版（Evolution）；鹏程·盘古多语言模型（mPanGu）；
- 支持 mindspore 和 pytorch 框架，支持 NPU 和 GPU 设备；提供 mindspore 和 pytorch 模型转换工具，可实现鹏程·盘古模型异构框架的快速切换及兼容生态发展。

## SDK API

<img src="./docs/pcl_pangu.png"/>

## 案例教程

- [dataset 数据预处理接口：提供了从 txt 文件到训练文件格式的转换（mindrecord 格式/bin文件）](docs/README_DATASET.md)
- [alpha 鹏程·盘古的基础大模型：分别在 mindspore 和 pytorch 框架下的使用教程，包括预训练、fine-tune、推理等](docs/README_PG.md)
- [Evolution alpha的增强版模型： Evolution 具有更强的任务理解与处理能力](docs/README_PGE.md)
- [mPangu alpha的多语言版预训练语言模型及多语言机器翻译模型：具有53种语言预训练语言模型能力及53种语言间的多对多机器翻译能力，在53种语言的单语语料进行预训练，然后在平行语料中持续学习得到，主要是以中文为中心的多语言大模型及机器翻译大模型](docs/README_MPG.md)
- [model_converter 模型转换模块：提供了把 mindspore 模型转为 pytorch 模型的 api，和将 pytorch 分布式模型转为单机模型、单机模型转为分布式模型的api](docs/README_CONVERTER.md)


## 红利！！！ 免费算力申请
如果您需要华为昇腾NPU或英伟达GPU算力对pcl_pangu进行试用和测试，请登录[[启智开源社区](https://git.openi.org.cn/)]，注册后进入本项目即可直接申请免费算力。


## 快速上手

- **模型推理**

提供了简单的推理流程，用户只需要输入需要生成的文本就可以在进行推理。首先需要在[模型下载页面](docs/README_MODELS.md)下载对应的模型，并且解压。下面展示如何快速使用 `alpha` 模型推理：

```python
from pcl_pangu.context import set_context
from pcl_pangu.model import alpha, evolution, mPangu

set_context(backend='mindspore')
config = alpha.model_config_npu(model='350M',load='350M/mode/path')
alpha.inference(config,input='四川的省会是?')
```

在 pytorch 框架上使用只需要把`set_context(backend='mindspore')` 改为 `backend='pytorch'`,并配置`model_config_gpu`

- **模型训练**

大模型的训练具有较高的入门门槛，不易上手，因此我们提供了一个简单的训练工具，可以快速的训练一个模型。用户只需要准备好训练数据，然后运行下面的代码：

```python
from pcl_pangu.context import set_context
from pcl_pangu.dataset import txt2mindrecord
from pcl_pangu.model import alpha, evolution, mPangu

set_context(backend='mindspore')
data_path = 'path/of/training/dataset'
txt2mindrecord(input_glob='your/txt/path/*.txt', output_prefix=data_path)
config = alpha.model_config_npu(model='350M',
                                load='path/to/save/ckpt',
                                data_path=data_path)
alpha.train(config)
```

- **模型 fine-tuning**

模型的 fine-tuning 流程基本和训练的流程一致，只需要更改为调用 `model.fine_tune()` ：

```python
from pcl_pangu.context import set_context
from pcl_pangu.dataset import txt2mindrecord
from pcl_pangu.model import alpha, evolution, mPangu

set_context(backend='mindspore')
data_path = 'path/of/training/dataset'
txt2mindrecord(input_glob='your/txt/path/*.txt', output_prefix=data_path)
config = alpha.model_config_npu(model='350M',
                                load='path/of/your/existing/ckpt',
                                data_path=data_path)
alpha.fine_tune(config)
```

## 环境搭建

- mindspore
  1、推荐使用 openi 启智社区提供的 npu 环境，[使用教程](docs/README_OPENI_MS.md)：

  2、裸机使用：需要安装 mindspore 环境，并且安装：

  ```bash
  pip install pcl_pangu
  ```

- pytorch

  如果你想在 pytorch 框架下使用，强烈建议使用我们预构建好的 docker 环境：

  ```bash
  docker pull yands/pangu-alpha-megatron-lm-nvidia-pytorch:20.03.2
  or 
  docker pull registry.cn-hangzhou.aliyuncs.com/pcl_hub/pangu_pytorch:pytorch.20.03.2
  ```
  容器安装包`pip install pcl_pangu`，并使用 `/opt/conda/bin/python`。

### 模型下载

所有模型文件下载地址：[请参考文件](./docs/README_MODELS.md)

#### 微信交流群
添加微信:鹏程.盘古α交流群:<img src="./docs/个人微信1.png" width="270"/><br/>


