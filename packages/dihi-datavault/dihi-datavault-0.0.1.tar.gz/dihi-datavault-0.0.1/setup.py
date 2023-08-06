# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dihi_datavault']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0',
 'colorama>=0.4.5,<0.5.0',
 'cryptography>=37.0.4,<38.0.0']

entry_points = \
{'console_scripts': ['datavault = dihi_datavault.cli:main']}

setup_kwargs = {
    'name': 'dihi-datavault',
    'version': '0.0.1',
    'description': 'Store encrypted files in your repository securely',
    'long_description': None,
    'author': 'Faraz Yashar',
    'author_email': 'fny@duke.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.2',
}


setup(**setup_kwargs)
