# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dslr']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0',
 'rich>=12.5.1,<13.0.0',
 'timeago>=1.0.15,<2.0.0',
 'tomli>=2.0.1,<3.0.0']

entry_points = \
{'console_scripts': ['dslr = dslr.cli:cli']}

setup_kwargs = {
    'name': 'dslr',
    'version': '0.2.0a0',
    'description': 'Take lightning fast snapshots of your local Postgres databases.',
    'long_description': '<br />\n<br />\n<p align="center">\n  <a href="https://github.com/mixxorz/DSLR">\n    <img width="281" height="84" src="https://user-images.githubusercontent.com/3102758/181914025-44bff27e-aac1-4d1b-a037-9fa98f9fed65.png">\n  </a>\n</p>\n<br />\n\n<p align="center">\n  <a href=""><img src="" alt=""></a>\n  <a href="https://badge.fury.io/py/dslr"><img src="https://badge.fury.io/py/dslr.svg" alt="PyPI version"></a>\n  <a href="https://pypi.python.org/pypi/dslr/"><img src="https://img.shields.io/pypi/pyversions/dslr.svg" alt="PyPI Supported Python Versions"></a>\n  <a href="https://github.com/mixxorz/dslr"><img src="https://github.com/mixxorz/dslr/actions/workflows/tests.yml/badge.svg" alt="GitHub Actions (Code quality and tests)"></a>\n\n</p>\n<br />\n\n---\n\nDatabase Snapshot, List, and Restore\n\nTake lightning fast snapshots of your local Postgres databases.\n\n## What is this?\n\nDSLR is a tool that allows you to quickly take and restore database snapshots\nwhen you\'re writing database migrations, switching branches, or messing with\nSQL.\n\nIt\'s meant to be a spiritual successor to\n[Stellar](https://github.com/fastmonkeys/stellar).\n\n**Important:** DSLR is intended for development use only. It is not advisable to\nuse DSLR on production databases.\n\n## Performance\n\nDSLR is much faster than the standard `pg_dump`/`pg_restore` approach to snapshots.\n\n<p align="center">\n  <img src="https://user-images.githubusercontent.com/3102758/182014327-1b13da6e-63ad-4bbe-817e-7d6c66befc98.png" alt="A chart comparing the execution time between DSLR and pg_dump/pg_restore. For snapshot and restore, DSLR took 4.125 seconds and 4.431 seconds respectively. pg_dump/pg_restore took 36.602 seconds and 13.257 seconds respectively.">\n</p>\n\nDSLR is 8x faster at taking snapshots and 3x faster at restoring snapshots compared to the `pg_dump`/`pg_restore` approach.\n\n<details>\n  <summary>Testing methodology</summary>\n  \n  I spun up Postgres 12.3 using Docker, created a test database, and filled it with 1GB of random data using this script:\n  \n  ```SQL\n  CREATE TABLE large_test (num1 bigint, num2 double precision, num3 double precision);\n\nINSERT INTO large*test (num1, num2, num3)\nSELECT round(random() * 10), random(), random() \\_ 142\nFROM generate_series(1, 20000000) s(i);\n\n```\n\nI used the following commands to measure the execution time:\n\n```\n\ntime dslr snapshot my-snapshot\ntime dslr restore my-snapshot\ntime pg_dump -Fc -f export.dump\ntime pg_restore --no-acl --no-owner export.dump\n\n```\n\nI ran each command three times and plotted the mean in the chart.\n\nHere\'s the raw data:\n\n| Command       | Run | Execution time (seconds) |\n| ------------- | --- | ------------------------ |\n| dslr snapshot | 1   | 4.797                    |\n|               | 2   | 4.650                    |\n|               | 3   | 2.927                    |\n| dslr restore  | 1   | 5.840                    |\n|               | 2   | 4.122                    |\n|               | 3   | 3.331                    |\n| pg_dump       | 1   | 37.345                   |\n|               | 2   | 36.227                   |\n|               | 3   | 36.233                   |\n| pg_restore    | 1   | 13.304                   |\n|               | 2   | 13.148                   |\n|               | 3   | 13.320                   |\n</details>\n\n## Install\n\n```\n\npip install DSLR psycopg2 # or psycopg2-binary\n\n````\n\nAdditionally, the DSLR `export` and `import` snapshot commands require `pg_dump`\nand `pg_restore` to be present in your `PATH`.\n\n## Configuration\n\nYou can tell DSLR which database to take snapshots of in a few ways:\n\n**DATABASE_URL**\n\nIf the `DATABASE_URL` environment variable is set, DSLR will use this to connect\nto your target database.\n\n```bash\nexport DATABASE_URL=postgres://username:password@host:port/database_name\n````\n\n**dslr.toml**\n\nIf a `dslr.toml` file exists in the current directory, DSLR will read its\nsettings from there. DSLR will prefer this over the environment variable.\n\n```toml\nurl = \'postgres://username:password@host:port/database_name\'\n```\n\n**`--url` option**\n\nFinally, you can explicitly pass the connection string via the `--url` option.\nThis will override any of the above settings.\n\n## Usage\n\n```\n$ dslr snapshot my-first-snapshot\nCreated new snapshot my-first-snapshot\n\n$ dslr restore my-first-snapshot\nRestored database from snapshot my-first-snapshot\n\n$ dslr list\n\n  Name                Created\n ────────────────────────────────────\n  my-first-snapshot   2 minutes ago\n\n$ dslr rename my-first-snapshot fresh-db\nRenamed snapshot my-first-snapshot to fresh-db\n\n$ dslr delete some-old-snapshot\nDeleted some-old-snapshot\n\n$ dslr export my-feature-test\nExported snapshot my-feature-test to my-feature-test_20220730-075650.dump\n\n$ dslr import snapshot-from-a-friend_20220730-080632.dump friend-snapshot\nImported snapshot friend-snapshot from snapshot-from-a-friend_20220730-080632.dump\n```\n\n## How does it work?\n\nDSLR takes snapshots by cloning databases using Postgres\' [Template\nDatabases](https://www.postgresql.org/docs/current/manage-ag-templatedbs.html)\nfunctionality. This is the main source of DSLR\'s speed.\n\nThis means that taking a snapshot is just creating a new database using the main\ndatabase as the template. Restoring a snapshot is just deleting the main\ndatabase and creating a new database using the snapshot database as the\ntemplate. So on and so forth.\n\n## License\n\nMIT\n',
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
