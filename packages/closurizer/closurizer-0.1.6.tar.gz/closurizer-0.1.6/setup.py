# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['closurizer']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=1.4.37,<2.0.0', 'click>=8,<9', 'petl>=1.7.10,<2.0.0']

entry_points = \
{'console_scripts': ['closurizer = closurizer.cli:main']}

setup_kwargs = {
    'name': 'closurizer',
    'version': '0.1.6',
    'description': 'Add closure expansion fields to kgx files following the Golr pattern',
    'long_description': None,
    'author': 'Kevin Schaper',
    'author_email': 'kevin@tislab.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
