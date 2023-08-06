# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ltchiptool',
 'ltchiptool.cli',
 'ltchiptool.models',
 'ltchiptool.soc',
 'ltchiptool.soc.ambz',
 'ltchiptool.soc.ambz.util',
 'ltchiptool.soc.ambz2',
 'ltchiptool.soc.bk72xx',
 'ltchiptool.soc.bk72xx.util',
 'ltchiptool.util',
 'uf2tool',
 'uf2tool.binpatch',
 'uf2tool.models']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0', 'colorama>=0.4.5,<0.5.0']

entry_points = \
{'console_scripts': ['ltchiptool = ltchiptool.cli:main']}

setup_kwargs = {
    'name': 'ltchiptool',
    'version': '1.0.0',
    'description': 'Tools for working with LT-supported IoT chips',
    'long_description': None,
    'author': 'Kuba Szczodrzyński',
    'author_email': 'kuba@szczodrzynski.pl',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
