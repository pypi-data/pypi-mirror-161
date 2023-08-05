# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['esdb',
 'esdb.client',
 'esdb.client.streams',
 'esdb.client.subscriptions',
 'esdb.generated']

package_data = \
{'': ['*']}

install_requires = \
['grpcio>=1.47.0,<2.0.0']

setup_kwargs = {
    'name': 'esdb',
    'version': '0.1.1',
    'description': 'gRPC client for EventStore DB',
    'long_description': None,
    'author': 'Andrii Kohut',
    'author_email': 'kogut.andriy@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
