# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['xdisplayselect']

package_data = \
{'': ['*']}

install_requires = \
['inquirer>=2.10.0,<3.0.0']

setup_kwargs = {
    'name': 'xdisplayselect',
    'version': '0.1.0',
    'description': 'Utility to simplify controlling monitors on linux WMs',
    'long_description': '# XDisplaySelect\n\nThis is a simple python utility allowing you to configure your monitors using xrandr.\n\nThis project is still heavily work in progress.\n',
    'author': 'ItsDrike',
    'author_email': 'itsdrike@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ItsDrike/xdisplayselect',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>3.9,<4',
}


setup(**setup_kwargs)
