# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['mappr', 'mappr.integrations']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'mappr',
    'version': '0.3.2',
    'description': '',
    'long_description': None,
    'author': 'Mateusz Klos',
    'author_email': 'novopl@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://novopl.github.io/mappr',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
