# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fxtrade', 'fxtrade.algorithm', 'fxtrade.interface']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'fxtrade',
    'version': '0.0.3',
    'description': '',
    'long_description': None,
    'author': 'wsuzume',
    'author_email': 'joshnobus@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
