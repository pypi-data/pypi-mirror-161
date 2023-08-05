# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hangarmc_hangar',
 'hangarmc_hangar.exception',
 'hangarmc_hangar.model',
 'hangarmc_hangar.parser']

package_data = \
{'': ['*']}

install_requires = \
['orjson>=3.7.7,<4.0.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'urllib3>=1.26.10,<2.0.0']

setup_kwargs = {
    'name': 'hangarmc-hangar',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Oskar',
    'author_email': '56176746+OskarZyg@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
