# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dictum_backend_vertica']

package_data = \
{'': ['*']}

install_requires = \
['dictum-core>=0.1.2,<0.2.0', 'sqlalchemy-vertica-python>=0.5.10,<0.6.0']

entry_points = \
{'dictum.backends': ['vertica = '
                     'dictum_backend_vertica.vertica_backend:VerticaBackend']}

setup_kwargs = {
    'name': 'dictum-backend-vertica',
    'version': '0.1.2',
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
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4',
}


setup(**setup_kwargs)
