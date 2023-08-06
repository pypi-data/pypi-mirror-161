# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['piecutter',
 'piecutter.commands',
 'piecutter.frameworks',
 'piecutter.templates']

package_data = \
{'': ['*']}

install_requires = \
['click==8.1.3', 'typer==0.6.1']

entry_points = \
{'console_scripts': ['piecutter = piecutter.main:app']}

setup_kwargs = {
    'name': 'piecutter-cli',
    'version': '0.1.0',
    'description': 'A CLI tool for building ML projects from research to production in no time.',
    'long_description': '',
    'author': 'g0nz4rth',
    'author_email': 'gonzarth@proton.me',
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
