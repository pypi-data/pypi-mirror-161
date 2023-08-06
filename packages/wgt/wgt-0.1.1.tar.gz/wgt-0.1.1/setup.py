# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wgt']

package_data = \
{'': ['*']}

install_requires = \
['requests', 'toolz']

entry_points = \
{'console_scripts': ['wgt = wgt.wgt:main']}

setup_kwargs = {
    'name': 'wgt',
    'version': '0.1.1',
    'description': 'Command line tool for quick API testing',
    'long_description': None,
    'author': 'Daniel Hjertholm',
    'author_email': 'daniel.hjertholm@icloud.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
