# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fingerprinter']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'pydantic>=1.9.0,<2.0.0']

entry_points = \
{'console_scripts': ['fingerprinter = fingerprinter.cli:main']}

setup_kwargs = {
    'name': 'uw-it-build-fingerprinter',
    'version': '0.2.6',
    'description': '',
    'long_description': None,
    'author': 'Tom Thorogood',
    'author_email': 'tom@tomthorogood.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
