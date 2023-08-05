# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cybergenetics',
 'cybergenetics.envs',
 'cybergenetics.envs.control',
 'cybergenetics.wrappers']

package_data = \
{'': ['*']}

install_requires = \
['gym>=0.25.0,<0.26.0', 'seaborn>=0.11.2,<0.12.0', 'torch>=1.12.0,<2.0.0']

setup_kwargs = {
    'name': 'cybergenetics',
    'version': '0.0.1',
    'description': 'Cybergenetics is a controlled simulating environment for chemical reaction networks (CRNs) and co-cultures.',
    'long_description': None,
    'author': 'Yi Zhang, Quentin Badolle',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
