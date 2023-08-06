# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['grafci']

package_data = \
{'': ['*']}

install_requires = \
['autopep8>=1.6.0,<2.0.0',
 'isort>=5.10.1,<6.0.0',
 'mkdocs>=1.3.1,<2.0.0',
 'pytest-cov>=3.0.0,<4.0.0',
 'pytest>=7.1.2,<8.0.0',
 'unify>=0.5,<0.6',
 'wemake-python-styleguide>=0.16.1,<0.17.0']

entry_points = \
{'console_scripts': ['grafci = grafci:main']}

setup_kwargs = {
    'name': 'grafci',
    'version': '0.1.0',
    'description': '',
    'long_description': '# grafci\n[![codecov](https://codecov.io/gh/nichmor/grafci/branch/master/graph/badge.svg?token=HOK1OKPEGE)](https://codecov.io/gh/nichmor/grafci)\n---\n\nWelcome to small and tiny CI engine',
    'author': 'nichitaelgraf',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/nichmor/grafci',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
