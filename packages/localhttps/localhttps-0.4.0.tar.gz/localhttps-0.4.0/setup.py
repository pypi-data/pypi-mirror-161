# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['localhttps',
 'localhttps.cert',
 'localhttps.cli',
 'localhttps.cli.commands',
 'localhttps.keychain',
 'localhttps.utils']

package_data = \
{'': ['*']}

install_requires = \
['aiofiles>=0.8.0,<0.9.0',
 'aiopath>=0.6.10,<0.7.0',
 'anyio>=3.5.0,<4.0.0',
 'asyncclick>=8.0.3,<9.0.0',
 'rich>=11.2.0,<12.0.0']

entry_points = \
{'console_scripts': ['localhttps = localhttps:main']}

setup_kwargs = {
    'name': 'localhttps',
    'version': '0.4.0',
    'description': 'HTTPS manager for local sites',
    'long_description': None,
    'author': 'Tarik02',
    'author_email': 'Taras.Fomin@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
