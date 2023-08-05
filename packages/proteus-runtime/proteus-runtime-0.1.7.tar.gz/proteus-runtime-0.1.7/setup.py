# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['proteus']

package_data = \
{'': ['*']}

install_requires = \
['certifi>=2022.6.15,<2023.0.0',
 'python-json-logger>=2.0.4,<3.0.0',
 'requests>=2.28.1,<3.0.0',
 'setuptools>=63.2.0,<64.0.0']

setup_kwargs = {
    'name': 'proteus-runtime',
    'version': '0.1.7',
    'description': '',
    'long_description': None,
    'author': None,
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
