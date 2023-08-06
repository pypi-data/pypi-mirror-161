# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['switchforpython']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'switchforpython',
    'version': '0.1.2',
    'description': 'Switch statements in python 3.x',
    'long_description': None,
    'author': 'Python Nerd',
    'author_email': 'prajwalmisc@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.0',
}


setup(**setup_kwargs)
