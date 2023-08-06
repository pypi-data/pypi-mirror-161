# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rho_plus']

package_data = \
{'': ['*']}

install_requires = \
['colour-science==0.3.16',
 'matplotlib>=3,<4',
 'numpy>=1.21,<2.0',
 'scipy>=1.7.0']

setup_kwargs = {
    'name': 'rho-plus',
    'version': '0.2.1',
    'description': 'Aesthetic and ergonomic enhancements to common Python data science tools',
    'long_description': None,
    'author': 'Nicholas Miklaucic',
    'author_email': 'nicholas.miklaucic@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
