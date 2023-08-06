# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dslr']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0', 'rich>=12.5.1,<13.0.0', 'timeago>=1.0.15,<2.0.0']

entry_points = \
{'console_scripts': ['dslr = dslr.cli:cli']}

setup_kwargs = {
    'name': 'dslr',
    'version': '0.1.0',
    'description': 'Take lightning fast snapshots of your local Postgres databases.',
    'long_description': '# DSLR\n\nDatabase Snapshot, List, and Restore\n\nTake lightning fast snapshots of your local Postgres databases.\n',
    'author': 'Mitchel Cabuloy',
    'author_email': 'mixxorz@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mixxorz/DSLR',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
