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
['orjson>=3.7.8,<4.0.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'urllib3>=1.26.11,<2.0.0']

setup_kwargs = {
    'name': 'hangarmc-hangar',
    'version': '1.0.0',
    'description': 'Hangar SDK for python',
    'long_description': '# hangarmc-hangar\n\npythonic type-hinted [hangar](https://github.com/HangarMC/Hangar) API wrapper\n\n## Installation\n\nhangarmc-hangar requires python 3.9 or above\n\n```shell\n# PIP3\npip3 install hangarmc-hangar\n# PIP\npip install hangarmc-hangar\n# Poetry\npoetry add hangarmc-hangar\n```\n\n## API\n\nAll functions and classes are properly type hinted and documented with quotes/comments. Please file an issue or pull\nrequest if any issues are found.\n\n### Basic Usage\n\n#### Example\n\n```python\nfrom hangarmc_hangar import Hangar, HangarApiException\n\n# Create an SDK instance\nhangar = Hangar()\n\ntry:\n    # Get all projects\n    projects = hangar.search_projects()\n    # Output data\n    print(f"Project amount: {projects.pagination.count}")\n    for project in projects.result:\n        print(project.name)\nexcept HangarApiException as e:\n    raise\n\n```\n\n#### Output\n\n```shell\n$ python sketch.py\nProject amount: 32\nCoolProject\nNotQuests\nEndBiomeFixer\n... and on\n```\n',
    'author': 'Oskar',
    'author_email': '56176746+OskarZyg@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/hangarmc-hangar/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
