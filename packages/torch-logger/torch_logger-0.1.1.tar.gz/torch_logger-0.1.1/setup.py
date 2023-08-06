# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['torch_logger']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'torch-logger',
    'version': '0.1.1',
    'description': 'A minimalist package for logging best values of metrics when training models with PyTorch',
    'long_description': '# torch_logger 🔥\n\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/torch_logger)\n\nThis minimalist package serves to log best values of performance metrics during the training of PyTorch models.\nThe idea is to automatically log the best value for each tracked metric such that it can be directly analyzed downstream (e.g. when using wandb) without the need to post-process the raw logged values to identify the overall best values and corresponding steps.\n\n## Usage:  \n\n```\n>>> from torch_logger import BestValueLogger\n>>> bv_log = BestValueLogger(\n        {\'val_loss\': False, \'val_roc\': True} # <-- provide flag if larger is better\n    )\n```\n\nLog values after each eval step:\n```\n    ... \n>>> bv_log([val_loss, val_roc], step=0)\n    ... \n>>> bv_log([val_loss, val_roc], step=1)\n    ...  \n>>> bv_log([val_loss, val_roc], step=2)\n```\n\nInspect the logger:\n```\n>>> bv_log\n\n::BestValueLogger::\nTracking the best values of the following metrics:\n{\n    "val_loss": false,\n    "val_roc": true\n}\n(key: metric, value: bool if larger is better)\nBest values and steps:\n{\n    "best_val_loss_value": 0.05,\n    "best_val_loss_step": 2,\n    "best_val_roc_value": 0.8,\n    "best_val_roc_step": 1\n}\n```\n\nUpdate your experiment logger (e.g. wandb) with best_values at the end of training\n```\n>>> wandb.log( bv_log.best_values ) \n```\n\n### Logging values without steps\n\nIn case you only wish to track values but not the corresponding steps, run: \n```\n>>> bvl = BestValueLogger({\'val_loss\': False, \'val_roc\':True}, log_step=False)\n```    \nPopulate logger with metrics: \n```\n>>> bvl([0.2,0.8], step=1)\n>>> bvl([0.2,0.9], step=2)\n```\nInspect:\n```\n>>> bvl\n::BestValueLogger::\nTracking the best values of the following metrics:\n{\n    "val_loss": false,\n    "val_roc": true\n}\n(key: metric, value: bool if larger is better)\nBest values:\n{\n    "best_val_loss_value": 0.2,\n    "best_val_roc_value": 0.9\n}\n```\n',
    'author': 'Michael Moor',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
