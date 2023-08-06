# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['arcane', 'arcane.core']

package_data = \
{'': ['*']}

install_requires = \
['google-cloud-core>=1.3,<2.0', 'typing-extensions>=3.7']

setup_kwargs = {
    'name': 'arcane-core',
    'version': '1.8.1',
    'description': 'Common utility functions',
    'long_description': None,
    'author': 'Arcane',
    'author_email': 'product@arcane.run',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
