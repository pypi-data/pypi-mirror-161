# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['enopios']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'enopios',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Simon Biggs',
    'author_email': 'simon.biggs@radiotherapy.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
