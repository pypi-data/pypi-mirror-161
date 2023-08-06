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
    'version': '0.1.3',
    'description': 'Work with MySQL databases asynchronously, and in context.',
    'long_description': '# MySQL Context Manager\n\n > Work with MySQL based databases asynchronously, using a context manager.\n\n[![PyPI version][pypi-image]][pypi-url]\n[![Build status][build-image]][build-url]\n[![Code coverage][coverage-image]][coverage-url]\n[![Support Python versions][versions-image]][versions-url]\n\n## Getting started\n\nYou can [get `mysql-context-manager` from PyPI](https://pypi.org/project/mysql-context-manager/),\nwhich means you can install it with pip easily:\n\n```bash\npython -m pip install mysql-context-manager\n```\n\n## Example\n\n```py\nfrom mysql_context_manager import MysqlConnector\n\nasync with MysqlConnector(hostname="localhost") as conn:\n    results = await conn.query("select username from users where is_bender = 1 order by username asc;")\nassert results[0]["username"] == "Aang"\nassert results[1]["username"] == "Katara"\nassert results[2]["username"] == "Toph"\n```\n\n## Example using SQLAlchemy\n\n```py\nfrom mysql_context_manager import MysqlConnector\nimport sqlalchemy\nfrom sqlalchemy.dialects import mysql\n\nmetadata = sqlalchemy.MetaData()\n\nusers = sqlalchemy.Table(\n    "users",\n    metadata,\n    sqlalchemy.Column("user_id", mysql.INTEGER(), autoincrement=True, nullable=False),\n    sqlalchemy.Column("username", mysql.VARCHAR(length=128), nullable=False),\n    sqlalchemy.Column("is_bender", mysql.SMALLINT(), autoincrement=False, nullable=True),\n    sqlalchemy.PrimaryKeyConstraint("user_id"),\n    mysql_default_charset="utf8mb4",\n    mysql_engine="InnoDB",\n)\n\nasync with MysqlConnector(hostname="localhost") as conn:\n    results = await conn.query(users.select().where(users.c.username == "Aang"))\nassert results[0]["username"] == "Aang"\nassert results[0]["is_bender"] == 1\n```\n\n## Changelog\n\nRefer to the [CHANGELOG.rst](CHANGELOG.rst) file.\n\n<!-- Badges -->\n\n[pypi-image]: https://img.shields.io/pypi/v/mysql-context-manager\n[pypi-url]: https://pypi.org/project/mysql-context-manager/\n[build-image]: https://github.com/idokendo/mysql-context-manager/actions/workflows/build.yaml/badge.svg\n[build-url]: https://github.com/idokendo/mysql-context-manager/actions/workflows/build.yaml\n[coverage-image]: https://codecov.io/ghidokendo/mysql-context-manager/branch/main/graph/badge.svg\n[coverage-url]: https://codecov.io/gh/idokendo/mysql-context-manager\n[versions-image]: https://img.shields.io/pypi/pyversions/mysql-context-manager\n[versions-url]: https://pypi.org/project/mysql-context-manager/\n',
    'author': 'IdoKendo',
    'author_email': 'ryuusuke@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/mysql-context-manager/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
