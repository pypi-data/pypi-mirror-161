# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['mysql_context_manager']

package_data = \
{'': ['*']}

install_requires = \
['PyMySQL>=1.0.2,<2.0.0', 'databases>=0.6.0,<0.7.0']

setup_kwargs = {
    'name': 'mysql-context-manager',
    'version': '0.1.0',
    'description': 'Work with MySQL databases asynchronously, and in context.',
    'long_description': None,
    'author': 'IdoKendo',
    'author_email': 'ryuusuke@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
