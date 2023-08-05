# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tegracli']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'Telethon>=1.24.0,<2.0.0',
 'click>=8.1.3,<9.0.0',
 'loguru>=0.6.0,<0.7.0',
 'pandas>=1.4.3,<2.0.0',
 'ujson>=5.4.0,<6.0.0']

entry_points = \
{'console_scripts': ['tegracli = tegracli.main:cli']}

setup_kwargs = {
    'name': 'tegracli',
    'version': '0.1.1a0',
    'description': 'A research-focused Telegram CLI application',
    'long_description': None,
    'author': 'Philipp Kessling',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
