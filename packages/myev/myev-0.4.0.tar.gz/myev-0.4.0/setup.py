# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['myev']

package_data = \
{'': ['*']}

install_requires = \
['validators>=0.20.0,<0.21.0']

setup_kwargs = {
    'name': 'myev',
    'version': '0.4.0',
    'description': 'Environment variables fetcher.',
    'long_description': 'myev\n====\n\nEnvironment variables fetcher.\n',
    'author': 'Łukasz Wieczorek',
    'author_email': 'wieczorek1990@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
