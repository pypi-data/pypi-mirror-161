# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['textprint', 'textprint.patterns']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'textprint',
    'version': '0.1.0',
    'description': 'Regex patterns. Simplified.',
    'long_description': '# Textprint\n\n> A Python library condensing popular patterns into simple objets to use\n\nEver hated long, tedious regex expressions? This package is made for you!\n',
    'author': 'Shadi Boomi',
    'author_email': 'shadi.boomi@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
