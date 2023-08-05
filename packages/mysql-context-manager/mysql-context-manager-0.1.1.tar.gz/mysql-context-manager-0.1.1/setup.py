# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['mysql_context_manager']

package_data = \
{'': ['*']}

install_requires = \
['PyMySQL>=1.0.2,<2.0.0', 'aiomysql>=0.1.1,<0.2.0', 'databases>=0.6.0,<0.7.0']

setup_kwargs = {
    'name': 'mysql-context-manager',
    'version': '0.1.1',
    'description': 'Work with MySQL databases asynchronously, and in context.',
    'long_description': '# MySQL Context Manager\n\nWork with MySQL based databases asynchronously, using a context manager.\n\n\n## Getting started\n\nYou can [get `mysql-context-manager` from PyPI](https://pypi.org/project/mysql-context-manager/),\nwhich means you can install it with pip easily:\n\n```bash\npython -m pip install mysql-context-manager\n```\n\n## Example\n\n```py\nfrom mysql_context_manager import MysqlConnector\n\nasync with MysqlConnector(hostname="localhost") as conn:\n    results = await conn.query("select username from users where is_bender = 1 order by username asc;")\nassert results[0]["username"] == "Aang"\nassert results[1]["username"] == "Katara"\nassert results[2]["username"] == "Toph"\n```\n',
    'author': 'IdoKendo',
    'author_email': 'ryuusuke@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
