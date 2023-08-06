# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytsas', 'pytsas.aggregate', 'pytsas.event']

package_data = \
{'': ['*'], 'pytsas': ['.git/*', '.git/hooks/*', '.git/info/*']}

install_requires = \
['pandas>=1.4.3,<2.0.0']

setup_kwargs = {
    'name': 'pytsas',
    'version': '0.0.1',
    'description': 'Package for python time-series analyses',
    'long_description': None,
    'author': 'mk.fschr',
    'author_email': 'mike.robin.fischer@web.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
