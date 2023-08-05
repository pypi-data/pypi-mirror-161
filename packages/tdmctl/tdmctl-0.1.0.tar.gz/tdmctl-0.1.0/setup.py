# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tdmctl']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.5,<0.5.0', 'columnar>=1.4.1,<2.0.0', 'typer[all]>=0.6.1,<0.7.0']

entry_points = \
{'console_scripts': ['tdmctl = tdmctl.main:app']}

setup_kwargs = {
    'name': 'tdmctl',
    'version': '0.1.0',
    'description': 'command line tool client for TouDoum-Framework',
    'long_description': '# tdmctl Cli for management of TouDoum-Framework',
    'author': 'msterhuj',
    'author_email': 'gabin.lanore@gmail.com',
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
