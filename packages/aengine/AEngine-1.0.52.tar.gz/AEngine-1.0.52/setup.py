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
             '.git/objects/0d/*',
             '.git/objects/24/*',
             '.git/objects/34/*',
             '.git/objects/46/*',
             '.git/objects/66/*',
             '.git/objects/6c/*',
             '.git/objects/6e/*',
             '.git/objects/6f/*',
             '.git/objects/79/*',
             '.git/objects/80/*',
             '.git/objects/8c/*',
             '.git/objects/8d/*',
             '.git/objects/b3/*',
             '.git/objects/cc/*',
             '.git/objects/d1/*',
             '.git/objects/d8/*',
             '.git/objects/d9/*',
             '.git/objects/e4/*',
             '.git/objects/f8/*',
             '.git/objects/f9/*',
             '.git/objects/pack/*',
             '.git/refs/heads/*',
             '.git/refs/remotes/origin/*']}

setup_kwargs = {
    'name': 'aengine',
    'version': '1.0.52',
    'description': 'Console applications Engine',
    'long_description': None,
    'author': 'alex',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
