# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['popol',
 'popol.cache',
 'popol.cache.backends',
 'popol.cache.serializers',
 'popol.context',
 'popol.db',
 'popol.db.sqlmodel',
 'popol.email',
 'popol.jobs',
 'popol.jobs.saq',
 'popol.templates.app',
 'popol.templates.app.extensions',
 'popol.templates.app.middleware',
 'popol.templates.app.routers',
 'popol.templates.app.settings',
 'popol.templates.tests']

package_data = \
{'': ['*'], 'popol': ['templates/*']}

install_requires = \
['asyncer>=0.0.1,<0.0.2',
 'fastapi>=0.78.0,<0.79.0',
 'pydantic[email]>=1.9.1,<2.0.0',
 'typer>=0.6.1,<0.7.0',
 'uvicorn[standard]>=0.18.2,<0.19.0']

extras_require = \
{'aiosmtplib': ['aiosmtplib>=1.1.6,<2.0.0'],
 'all': ['redis>=4.3.4,<5.0.0',
         'saq>=0.8.0,<0.9.0',
         'sqlmodel>=0.0.6,<0.0.7',
         'pyhumps>=3.7.2,<4.0.0',
         'aiosmtplib>=1.1.6,<2.0.0'],
 'background_jobs': ['saq>=0.8.0,<0.9.0'],
 'cache': ['redis>=4.3.4,<5.0.0'],
 'orm': ['sqlmodel>=0.0.6,<0.0.7', 'pyhumps>=3.7.2,<4.0.0'],
 'redis': ['redis>=4.3.4,<5.0.0'],
 'saq': ['saq>=0.8.0,<0.9.0'],
 'sqlmodel': ['sqlmodel>=0.0.6,<0.0.7', 'pyhumps>=3.7.2,<4.0.0']}

entry_points = \
{'console_scripts': ['popol = popol.__main__:popol'],
 'popol.commands': ['saq = popol.jobs.saq.cli:saq']}

setup_kwargs = {
    'name': 'popol',
    'version': '0.4.0',
    'description': 'Adding new power to your FastAPI application ⛅',
    'long_description': '# Popol ⛅\n\n> Adding new power to your FastAPI application ⛅\n\nPopol is a library that provides as-is tools for use on FastAPI.\n\nThis project aims to provide APIs to support your FastAPI projects without breaking existing projects. This is another version of the [Fastack](https://github.com/fastack-dev/fastack) project. Overall the available APIs are not much different from the [Fastack plugins](https://github.com/fastack-dev).\n\n## Features 🌟\n\n- [x] Project Layout\n- [x] Command Line Interface (like `flask` command)\n- [x] Pagination\n- Cache Framework\n\n    - Backends\n\n        - [x] Redis (Sync/Async)\n        - [ ] Memcached\n\n    - Serializers\n\n        - [x] JSON\n        - [x] Pickle\n        - [ ] MsgPack\n\n- ORM Integration\n\n    - [x] SQLModel (Async/Sync)\n    - [ ] Tortoise ORM\n\n- ODM Integration\n\n    - [ ] MongoEngine\n\n- [x] SMTP client (using aiosmtplib) to send emails.\n- Background Jobs:\n\n    - [x] SAQ queue support for task scheduling\n\n\n## Installation 📚\n\n```\npip install popol>=0.4.0\n```\n\n## Documentation 📖\n\nNot available at this time, please learn from the [examples](https://github.com/aprilahijriyan/popol/tree/main/examples).\n',
    'author': 'aprilahijriyan',
    'author_email': 'hijriyan23@gmail.com',
    'maintainer': 'aprilahijriyan',
    'maintainer_email': 'hijriyan23@gmail.com',
    'url': 'https://github.com/aprilahijriyan/popol',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
