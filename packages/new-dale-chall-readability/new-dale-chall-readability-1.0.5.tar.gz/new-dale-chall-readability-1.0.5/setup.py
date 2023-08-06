# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['new_dale_chall_readability']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'new-dale-chall-readability',
    'version': '1.0.5',
    'description': 'An implementation of the New Dale-Chall readability formula which strictly follows the specification.',
    'long_description': '[![Tests and type-checks](https://github.com/public-law/new-dale-chall-readability/actions/workflows/python-app.yml/badge.svg)](https://github.com/public-law/new-dale-chall-readability/actions/workflows/python-app.yml) [![Maintainability](https://api.codeclimate.com/v1/badges/ef1198fa2d9246aa3c7d/maintainability)](https://codeclimate.com/github/public-law/new-dale-chall-readability/maintainability)\n\n\n# The new Dale-Chall readability formula\n\nIn a nutshell:\n\n```python\nIn [1]: from new_dale_chall_readability import cloze_score, reading_level\n\nIn [2]: text = (\n   ...:     \'Latin for "friend of the court." It is advice formally offered \'\n   ...:     \'to the court in a brief filed by an entity interested in, but not \'\n   ...:     \'a party to, the case.\'\n   ...:     )\n\nIn [3]: cloze_score(text)\nOut[3]: 42.46652\n\nIn [4]: reading_level(text)\nOut[4]: \'5-6\'\n```\n\n\nAn implementation that follows the specification as closely as\npossible. Created by referring to a copy of\nthe most recent publication (Chall & Dale, 1995).\n\n\n## References\n\nChall, J., & Dale, E. (1995). _Readability revisited: The new Dale-Chall readability formula_.\nBrookline Books.\n',
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
