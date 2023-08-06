# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['torch_logger']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'torch-logger',
    'version': '0.1.0',
    'description': 'A minimalist package for logging best values of metrics when training models with PyTorch',
    'long_description': None,
    'author': 'michael',
    'author_email': 'michael.d.moor@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
