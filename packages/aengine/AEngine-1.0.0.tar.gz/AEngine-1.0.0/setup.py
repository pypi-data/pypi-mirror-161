# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aengine']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'aengine',
    'version': '1.0.0',
    'description': 'Console applications Engine',
    'long_description': None,
    'author': 'alex',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
