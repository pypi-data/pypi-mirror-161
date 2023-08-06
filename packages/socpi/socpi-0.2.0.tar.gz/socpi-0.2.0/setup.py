# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['socpi']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'socpi',
    'version': '0.2.0',
    'description': 'A socket api framework',
    'long_description': None,
    'author': 'Grzegorz Koperwas',
    'author_email': 'admin@grzegorzkoperwas.site',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
