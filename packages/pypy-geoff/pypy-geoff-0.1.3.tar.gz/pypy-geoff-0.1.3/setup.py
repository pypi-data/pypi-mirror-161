# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pypy_geoff']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pypy-geoff',
    'version': '0.1.3',
    'description': '',
    'long_description': '# Example Python Package\n\nFollowing this article: https://mathspp.com/blog/how-to-create-a-python-package-in-2022\n\n## Notes\n\n**ZSH**\nIn zsh, it looks like you need to quote poetry packages:\n\n```\npoetry add -D scriv[toml]\n$ zsh: no matches found: scriv[toml]\n```\n\n```\npoetry add -D "scriv[toml]"\n$ ... installed ...\n```\n',
    'author': 'Geoff Dutton',
    'author_email': 'g.dutton@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
