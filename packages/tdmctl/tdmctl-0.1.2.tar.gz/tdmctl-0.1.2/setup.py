# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tdmctl', 'tdmctl.commands']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'colorama>=0.4.5,<0.5.0',
 'columnar>=1.4.1,<2.0.0',
 'typer[all]>=0.6.1,<0.7.0']

entry_points = \
{'console_scripts': ['tdmctl = tdmctl.main:app']}

setup_kwargs = {
    'name': 'tdmctl',
    'version': '0.1.2',
    'description': 'command line tool client for TouDoum-Framework',
    'long_description': '# tdmctl Cli for management of TouDoum-Framework\n\n## Sample of config file\n```yaml\ncurrent_context: cluster1\ncontext:\n    cluster1: \n        host: localhost\n        user: admin\n        pass: admin\n```\n## .tdmctl folder structure\n```yaml\n.tdmctl:\n  config.yml:\n  modules:\n    <context-name1>:\n      <module-name1>:\n        main.py:\n    <context-name2>:\n      <module-name1>:\n        main.py:\n      <module-name2>:\n        main.py:\n```',
    'author': 'msterhuj',
    'author_email': 'gabin.lanore@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://toudoum-framework.github.io/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
