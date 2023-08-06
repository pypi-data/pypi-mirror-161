# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mhered_test_pkg']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'mhered-test-pkg',
    'version': '0.1.0',
    'description': 'A simple test package to practice on',
    'long_description': None,
    'author': 'Manuel Heredia',
    'author_email': 'manolo.heredia@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
