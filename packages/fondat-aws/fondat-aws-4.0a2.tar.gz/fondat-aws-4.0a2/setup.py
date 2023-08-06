# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fondat', 'fondat.aws']

package_data = \
{'': ['*']}

install_requires = \
['aiobotocore>=2.3,<3.0', 'fondat>=4.0a5,<5.0']

setup_kwargs = {
    'name': 'fondat-aws',
    'version': '4.0a2',
    'description': 'Fondat package for Amazon Web Services.',
    'long_description': '# fondat-aws\n\n[![PyPI](https://badge.fury.io/py/fondat-aws.svg)](https://badge.fury.io/py/fondat-aws)\n[![Python](https://img.shields.io/pypi/pyversions/fondat-core)](https://python.org/)\n[![GitHub](https://img.shields.io/badge/github-main-blue.svg)](https://github.com/fondat/fondat-aws/)\n[![Test](https://github.com/fondat/fondat-aws/workflows/test/badge.svg)](https://github.com/fondat/fondat-aws/actions?query=workflow/test)\n[![License](https://img.shields.io/github/license/fondat/fondat-aws.svg)](https://github.com/fondat/fondat-aws/blob/main/LICENSE)\n[![Black](https://img.shields.io/badge/code%20style-black-black.svg)](https://github.com/psf/black)\n\nFondat package for Amazon Web Services.\n\n## Develop\n\n```\npoetry install\npoetry run pre-commit install\n```\n\n## Test\n\n```\npoetry run pytest\n```\n',
    'author': 'fondat-aws authors',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/fondat/fondat-aws/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
