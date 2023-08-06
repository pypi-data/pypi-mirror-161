# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['managed_service_fixtures', 'managed_service_fixtures.services']

package_data = \
{'': ['*']}

install_requires = \
['filelock>=3.7.1,<4.0.0',
 'importlib-metadata>=4.12.0,<5.0.0',
 'mirakuru>=2.4.2,<3.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'pytest-asyncio>=0.19.0,<0.20.0',
 'pytest-xdist>=2.5.0,<3.0.0',
 'pytest>=7.1.0,<8.0.0']

setup_kwargs = {
    'name': 'managed-service-fixtures',
    'version': '0.1.1',
    'description': 'Pytest fixtures to manage external services such as Cockroach DB, Vault, or Redis',
    'long_description': None,
    'author': 'Noteable Engineering',
    'author_email': 'engineering-backend@noteable.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
