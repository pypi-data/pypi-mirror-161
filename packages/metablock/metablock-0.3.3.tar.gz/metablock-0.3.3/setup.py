# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['metablock']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0']

setup_kwargs = {
    'name': 'metablock',
    'version': '0.3.3',
    'description': 'Metablock cloud python client',
    'long_description': '# A Python Client for Metablock API\n\n[![PyPI version](https://badge.fury.io/py/metablock.svg)](https://badge.fury.io/py/metablock)\n[![Python versions](https://img.shields.io/pypi/pyversions/metablock.svg)](https://pypi.org/project/metablock)\n[![Build](https://github.com/quantmind/metablock-py/workflows/build/badge.svg)](https://github.com/quantmind/metablock-py/actions?query=workflow%3Abuild)\n[![codecov](https://codecov.io/gh/quantmind/metablock-py/branch/master/graph/badge.svg?token=EAdSVpD0Af)](https://codecov.io/gh/quantmind/metablock-py)\n\nThis is an asynchronous python client for [metablock API](https://api.metablock.io/v1/docs).\n\n## Installation\n\nThis is a simple python package you can install via pip:\n\n```\npip install metablock\n```\n\n## Usage\n\nCreate the client\n\n```python\nfrom metablock import Metablock\n\ncli = Metablock()\n\n# get the user associated with the API token\nuser = await cli.get_user()\n```\n',
    'author': 'Luca',
    'author_email': 'luca@quantmind.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
