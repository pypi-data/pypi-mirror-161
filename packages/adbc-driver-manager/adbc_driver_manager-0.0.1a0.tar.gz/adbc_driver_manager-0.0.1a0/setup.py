# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['adbc_driver_manager', 'adbc_driver_manager.tests']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'adbc-driver-manager',
    'version': '0.0.1a0',
    'description': '',
    'long_description': None,
    'author': 'David Li',
    'author_email': 'li.davidm96@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
