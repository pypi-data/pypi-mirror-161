# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['deck', 'modular', 'utils']

package_data = \
{'': ['*']}

install_requires = \
['ecl2df>=0.16.1,<0.17.0',
 'h5py>=3.6.0,<4.0.0',
 'libecl>=2.13.1,<3.0.0',
 'pandas>=1.4.1,<2.0.0',
 'python-json-logger>=2.0.1,<3.0.0',
 'readchar>=3.0.4,<4.0.0',
 'tables>=3.7.0,<4.0.0',
 'tabulate>=0.8.9,<0.9.0',
 'tqdm>=4.61.0,<5.0.0']

setup_kwargs = {
    'name': 'proteus-preprocessing',
    'version': '0.1.9',
    'description': '',
    'long_description': None,
    'author': None,
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
