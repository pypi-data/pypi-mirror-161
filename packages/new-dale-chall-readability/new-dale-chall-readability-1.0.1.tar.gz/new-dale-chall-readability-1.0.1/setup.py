# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['new_dale_chall_readability']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'new-dale-chall-readability',
    'version': '1.0.1',
    'description': 'An implementation of the New Dale-Chall readability formula which strictly follows the specification.',
    'long_description': '[![Tests and type-checks](https://github.com/public-law/new-dale-chall-readability/actions/workflows/python-app.yml/badge.svg)](https://github.com/public-law/new-dale-chall-readability/actions/workflows/python-app.yml)\n\n\n# The new Dale-Chall readability formula\nA fresh reimplementation of the formula. Created by referring to a paper copy of\ntheir most recent publication (Chall & Dale, 1995).\n\n\n## References\n\nChall, J., & Dale, E. (1995). _Readability revisited: The new Dale-Chall readability formula_.\nBrookline Books.\n',
    'author': 'Robb Shecter',
    'author_email': 'robb@public.law',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/public-law/new-dale-chall-readability',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
