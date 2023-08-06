# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dictum_backend_vertica']

package_data = \
{'': ['*']}

install_requires = \
['sqlalchemy-vertica-python>=0.5.10,<0.6.0']

setup_kwargs = {
    'name': 'dictum-backend-vertica',
    'version': '0.1.0',
    'description': 'Vertica backend for Dictum',
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
