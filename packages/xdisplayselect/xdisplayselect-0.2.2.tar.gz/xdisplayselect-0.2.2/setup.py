# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['xdisplayselect']

package_data = \
{'': ['*']}

install_requires = \
['inquirer>=2.10.0,<3.0.0']

entry_points = \
{'console_scripts': ['xdisplayselect = xdisplayselect.__main__:cli']}

setup_kwargs = {
    'name': 'xdisplayselect',
    'version': '0.2.2',
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
    'entry_points': entry_points,
    'python_requires': '>3.9,<4',
}


setup(**setup_kwargs)
