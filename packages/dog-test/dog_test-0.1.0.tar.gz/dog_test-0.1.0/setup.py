# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dog_test']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'dog-test',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'britt frenkel',
    'author_email': 'britt@redefine.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
