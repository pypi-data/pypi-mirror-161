# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dictum_backend_postgres']

package_data = \
{'': ['*']}

install_requires = \
['dictum-core>=0.1,<0.2', 'psycopg2-binary>=2.9.3,<3.0.0']

setup_kwargs = {
    'name': 'dictum-backend-postgres',
    'version': '0.1.0',
    'description': 'Postgres backend for Dictum',
    'long_description': None,
    'author': 'Mikhail Akimov',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
