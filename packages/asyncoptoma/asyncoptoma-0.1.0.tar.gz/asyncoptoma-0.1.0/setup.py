# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['asyncoptoma']

package_data = \
{'': ['*']}

install_requires = \
['bs4>=0.0.1,<0.0.2', 'httpx>=0.23.0,<0.24.0']

setup_kwargs = {
    'name': 'asyncoptoma',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Sebastian Lübke',
    'author_email': 'luebke@gonicus.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
