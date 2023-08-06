# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastapi_healthchecks',
 'fastapi_healthchecks.api',
 'fastapi_healthchecks.checks']

package_data = \
{'': ['*']}

install_requires = \
['fastapi>=0.70.1', 'pydantic>=1.9']

extras_require = \
{'all': ['aio-pika>=7',
         'aiohttp[speedups]>=3,<4',
         'aiorgwadmin>=1,<2',
         'asyncpg>=0.25.0',
         'redis>=4,<5'],
 'ceph': ['aiorgwadmin>=1,<2'],
 'http': ['aiohttp[speedups]>=3,<4'],
 'postgres': ['asyncpg>=0.25.0'],
 'rabbitmq': ['aio-pika>=7'],
 'redis': ['redis>=4,<5']}

setup_kwargs = {
    'name': 'fastapi-healthchecks',
    'version': '1.0.3',
    'description': 'FastAPI Healthchecks',
    'long_description': '# fastapi-healthchecks\nFastAPI healthchecks\n',
    'author': 'RockITSoft',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
