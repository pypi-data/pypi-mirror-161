# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['pcl_pangu',
 'pcl_pangu.context',
 'pcl_pangu.dataset',
 'pcl_pangu.model',
 'pcl_pangu.model_converter',
 'pcl_pangu.model.alpha',
 'pcl_pangu.model.evolution',
 'pcl_pangu.model.mPangu',
 'pcl_pangu.tokenizer',
 'pcl_pangu.tokenizer.bpe_4w_pcl',
 'pcl_pangu.tokenizer.spm_13w',
 'pcl_pangu.model.panguAlpha_pytorch',
 'pcl_pangu.model.panguAlpha_pytorch.megatron',
 'pcl_pangu.model.panguAlpha_pytorch.megatron.data',
 'pcl_pangu.model.panguAlpha_pytorch.megatron.fp16',
 'pcl_pangu.model.panguAlpha_pytorch.megatron.fused_kernels',
 'pcl_pangu.model.panguAlpha_pytorch.megatron.model',
 'pcl_pangu.model.panguAlpha_pytorch.megatron.mpu',
 'pcl_pangu.model.panguAlpha_pytorch.megatron.tokenizer',
 'pcl_pangu.model.panguAlpha_pytorch.tools',
 'pcl_pangu.model.panguAlpha_mindspore',
 'pcl_pangu.model.panguAlpha_mindspore.src',
]

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.17.5,<2.0.0',
 'sentencepiece>=0.1.0',
 'jieba>=0.32.0',
 'loguru>=0.3.0']

extras_require = \
{':python_version < "3.7"': ['dataclasses==0.6']}

setup_kwargs = {
    'name': 'pcl_pangu',
    'version': '1.0.3',
    'description': 'pcl_pangu',
    'long_description': '# pcl_pangu ',
    'author': '2022 PCL',
    'author_email': 'pcl.openi@pcl.ac.cn',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://git.openi.org.cn/PCL-Platform.Intelligence/pcl_pangu',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
