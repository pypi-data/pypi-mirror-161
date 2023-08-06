# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aengine']

package_data = \
{'': ['*'],
 'aengine': ['.git/*',
             '.git/hooks/*',
             '.git/info/*',
             '.git/logs/*',
             '.git/logs/refs/heads/*',
             '.git/logs/refs/remotes/origin/*',
             '.git/objects/pack/*',
             '.git/refs/heads/*',
             '.git/refs/remotes/origin/*']}

setup_kwargs = {
    'name': 'aengine',
    'version': '1.0.1',
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
