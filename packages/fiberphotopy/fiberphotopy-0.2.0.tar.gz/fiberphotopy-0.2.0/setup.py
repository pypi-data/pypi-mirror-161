# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fiberphotopy',
 'fiberphotopy.plotting',
 'fiberphotopy.preprocess',
 'fiberphotopy.stats']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'matplotlib>=3.5.2,<4.0.0',
 'numpy>=1.23.1,<2.0.0',
 'pandas>=1.4.3,<2.0.0',
 'pingouin>=0.5.2,<0.6.0',
 'ruamel.yaml>=0.17.21,<0.18.0',
 'scipy>=1.8.1,<2.0.0',
 'seaborn>=0.11.2,<0.12.0']

setup_kwargs = {
    'name': 'fiberphotopy',
    'version': '0.2.0',
    'description': 'Package for loading and processing fiber photometry data',
    'long_description': None,
    'author': 'kpuhger',
    'author_email': 'krpuhger@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
