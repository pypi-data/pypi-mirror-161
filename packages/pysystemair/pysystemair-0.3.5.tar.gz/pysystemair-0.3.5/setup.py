# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pysystemair']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.9.0,<2.0.0', 'pymodbus>=2.5.3,<3.0.0', 'python-box>=6.0.2,<7.0.0']

setup_kwargs = {
    'name': 'pysystemair',
    'version': '0.3.5',
    'description': 'Python package to interface a SystamAir SAVE VTR ventilation through modbus. Heavily insipired by pyflexit (https://github.com/Sabesto/pyflexit). Made with the purpose of working with a home assistant component',
    'long_description': None,
    'author': 'mvheimburg',
    'author_email': 'heimburg@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
