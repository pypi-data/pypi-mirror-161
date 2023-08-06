# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyltd2']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.23.1,<2.0.0', 'pandas>=1.4.3,<2.0.0', 'tqdm>=4.64.0,<5.0.0']

setup_kwargs = {
    'name': 'pyltd2',
    'version': '1.0.0rc0',
    'description': 'Client package for the download of Legion TD 2 game data.',
    'long_description': None,
    'author': 'GCidd',
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
