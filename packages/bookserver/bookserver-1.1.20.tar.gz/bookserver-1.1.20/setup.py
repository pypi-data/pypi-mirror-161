# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bookserver', 'bookserver.internal', 'bookserver.routers']

package_data = \
{'': ['*'], 'bookserver': ['templates/auth/*']}

install_requires = \
['Jinja2<3.1.0',
 'SQLAlchemy>=1.0.0,<2.0.0',
 'aiofiles>=0.8.0,<0.9.0',
 'aioredis>=2.0.0,<3.0.0',
 'aiosqlite>=0.17.0,<0.18.0',
 'alembic>=1.0.0,<2.0.0',
 'async-timeout>=3.0.0,<4.0.0',
 'asyncpg>=0.24.0,<0.25.0',
 'bleach>=4.0.0,<5.0.0',
 'celery[redis]>=5.0.0,<6.0.0',
 'fastapi-login>=1.7.0,<2.0.0',
 'fastapi>=0.68.0,<0.69.0',
 'multi-await>=1.0.0,<2.0.0',
 'pydal>=20210215.1',
 'pyhumps>=3.0.0,<4.0.0',
 'python-dateutil>=2.0.0,<3.0.0',
 'python-multipart>=0.0.5,<0.0.6',
 'redis>=4.0.0,<5.0.0',
 'runestone>=6.0.0,<7.0.0',
 'uvicorn[standard]>=0.17.0,<0.18.0']

extras_require = \
{':sys_platform != "win32"': ['gunicorn>=20.0.0,<21.0.0']}

entry_points = \
{'console_scripts': ['bookserver = bookserver.__main__:run']}

setup_kwargs = {
    'name': 'bookserver',
    'version': '1.1.20',
    'description': 'A new Runestone Server Framework',
    'long_description': '*******************************************\nNew FastAPI-based Book Server for Runestone\n*******************************************\nThe BookServer is a next-generation server for the `Runestone platform <https://runestone.academy/>`_. The goal of this project is to replace the parts of the web2py-based RunestoneServer. For more information, see the `full documentation <https://bookserver.readthedocs.io/en/latest/>`_.\n\nWe would love development help on this; see the `developer docs <https://bookserver.readthedocs.io/en/latest/docs/dev_toctree.html>`_.\n\nTODO: A nice image of a book or something eye-catching.',
    'author': 'Brad Miller',
    'author_email': 'bonelake@mac.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8.0,<4.0.0',
}


setup(**setup_kwargs)
