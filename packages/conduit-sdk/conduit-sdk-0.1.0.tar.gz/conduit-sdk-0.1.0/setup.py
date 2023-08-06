# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['conduit_sdk', 'conduit_sdk.block', 'conduit_sdk.common']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'conduit-sdk',
    'version': '0.1.0',
    'description': 'Conduit sdk is a collection of utils for development of conduit external block.',
    'long_description': None,
    'author': 'Conduit.app',
    'author_email': 'support@getconduit.app',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
