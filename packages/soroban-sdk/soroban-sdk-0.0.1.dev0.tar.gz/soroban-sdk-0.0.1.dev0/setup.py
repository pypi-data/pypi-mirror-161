# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['soroban_sdk']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'soroban-sdk',
    'version': '0.0.1.dev0',
    'description': '',
    'long_description': None,
    'author': 'Jun Luo',
    'author_email': '4catcode@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
