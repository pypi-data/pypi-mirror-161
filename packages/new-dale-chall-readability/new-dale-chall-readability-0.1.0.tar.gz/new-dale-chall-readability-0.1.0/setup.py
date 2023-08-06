# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['new_dale_chall_readability']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'new-dale-chall-readability',
    'version': '0.1.0',
    'description': 'A reimplementation of the New Dale-Chall readability metric. Based on the book, _Readability Revisited, The New Dale-Chall Readability Formula_, (1995) by Chall and Dale.',
    'long_description': None,
    'author': 'Robb Shecter',
    'author_email': 'robb@public.law',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
