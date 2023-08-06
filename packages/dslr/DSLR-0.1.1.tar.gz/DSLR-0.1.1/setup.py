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
    'version': '0.1.1',
    'description': 'Take lightning fast snapshots of your local Postgres databases.',
    'long_description': '<br />\n<br />\n<p align="center">\n  <img width="281" height="84" src="https://user-images.githubusercontent.com/3102758/181914025-44bff27e-aac1-4d1b-a037-9fa98f9fed65.png">\n</p>\n<br />\n\n<p align="center">\n  <a href=""><img src="" alt=""></a>\n  <a href="https://badge.fury.io/py/dslr"><img src="https://badge.fury.io/py/dslr.svg" alt="PyPI version"></a>\n  <a href="https://pypi.python.org/pypi/dslr/"><img src="https://img.shields.io/pypi/pyversions/dslr.svg" alt="PyPI Supported Python Versions"></a>\n  <a href="https://github.com/mixxorz/dslr"><img src="https://github.com/mixxorz/dslr/actions/workflows/tests.yml/badge.svg" alt="GitHub Actions (Code quality and tests)"></a>\n\n</p>\n<br />\n\n---\n\nDatabase Snapshot, List, and Restore\n\nTake lightning fast snapshots of your local Postgres databases.\n\n## What is this?\n\nDSLR is a tool that allows you to quickly take and restore database snapshots\nwhen you\'re writing database migrations, switching branches, or messing with\nSQL.\n\nIt\'s meant to be a spiritual successor to\n[Stellar](https://github.com/fastmonkeys/stellar).\n\n**Important:** DSLR is intended for development use only. It is not advisable to\nuse DSLR on production databases.\n\n## Performance\n\nDSLR is really fast.\n\n_Impressive chart goes here_\n\n## Install\n\n```\npip install DSLR\n```\n\nDSLR requires that the Postgres client binaries (`psql`, `createdb`, `dropdb`)\nare present in your `PATH`. DSLR uses them to interact with Postgres.\n\n## Usage\n\nFirst you need to point DSLR to the database you want to take snapshots of. The\neasiest way to do this is to export the `DATABASE_URL` environment variable.\n\n```bash\nexport DATABASE_URL=postgres://username:password@host:port/database_name\n```\n\nAlternatively, you can pass the connection string via the `--db` option.\n\nYou\'re ready to use DSLR!\n\n```\n$ dslr snapshot my-first-snapshot\nCreated new snapshot my-first-snapshot\n\n$ dslr restore my-first-snapshot\nRestored database from snapshot my-first-snapshot\n\n$ dslr list\n\n  Name                Created\n ────────────────────────────────────\n  my-first-snapshot   2 minutes ago\n\n$ dslr rename my-first-snapshot fresh-db\nRenamed snapshot my-first-snapshot to fresh-db\n\n$ dslr delete some-old-snapshot\nDeleted some-old-snapshot\n\n$ dslr export my-feature-test\nExported snapshot my-feature-test to my-feature-test_20220730-075650.dump\n\n$ dslr import snapshot-from-a-friend_20220730-080632.dump friend-snapshot\nImported snapshot friend-snapshot from snapshot-from-a-friend_20220730-080632.dump\n```\n\n## How does it work?\n\nDSLR takes snapshots by cloning databases using Postgres\' [Template\nDatabases](https://www.postgresql.org/docs/current/manage-ag-templatedbs.html)\nfunctionality. This is the main source of DSLR\'s speed.\n\nThis means that taking a snapshot is just creating a new database using the main\ndatabase as the template. Restoring a snapshot is just deleting the main\ndatabase and creating a new database using the snapshot database as the\ntemplate. So on and so forth.\n\n## License\n\nMIT\n',
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
