# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pypy_geoff']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pypy-geoff',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Geoff Dutton',
    'author_email': 'g.dutton@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
