# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_broker']

package_data = \
{'': ['*']}

install_requires = \
['asyncio>=3.4.3,<4.0.0',
 'nonebot-adapter-onebot>=2.0.0-beta.1,<3.0.0',
 'nonebot-plugin-apscheduler>=0.1.2,<0.2.0',
 'nonebot2>=2.0.0-beta.2,<3.0.0',
 'ruamel.yaml>=0.17.21,<0.18.0']

setup_kwargs = {
    'name': 'nonebot-plugin-broker',
    'version': '0.4.1',
    'description': 'a plugin for nonebot',
    'long_description': None,
    'author': 'mwbimh',
    'author_email': 'mwbimh@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.13,<4.0.0',
}


setup(**setup_kwargs)
