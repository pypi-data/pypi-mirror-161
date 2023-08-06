# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytfbot']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=1.4.39,<2.0.0']

setup_kwargs = {
    'name': 'pytfbot',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'tonio213',
    'author_email': '1956749+tonio213@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
