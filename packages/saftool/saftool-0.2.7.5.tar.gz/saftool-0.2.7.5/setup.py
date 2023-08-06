# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['saftool']

package_data = \
{'': ['*']}

install_requires = \
['joblib>=1.0.1,<2.0.0',
 'py7zr>=0.17.2,<0.18.0',
 'python-dateutil>=2.8.1,<3.0.0',
 'requests>=2.24.0,<3.0.0',
 'tqdm>=4.59.0,<5.0.0']

setup_kwargs = {
    'name': 'saftool',
    'version': '0.2.7.5',
    'description': '',
    'long_description': '# saftool',
    'author': 'Asdil Fibrizo',
    'author_email': 'jpl4job@126.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Asdil/saftool',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
