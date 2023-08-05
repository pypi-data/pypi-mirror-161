# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['creating_package_test']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'creating-package-test',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Claudio Canales',
    'author_email': 'klaudioz@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
