# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['multicast_expert']

package_data = \
{'': ['*']}

install_requires = \
['netifaces<1.0.0']

setup_kwargs = {
    'name': 'multicast-expert',
    'version': '0.0.1',
    'description': 'A library to take the fiddly parts out of multicast networking!',
    'long_description': None,
    'author': 'Jamie Smith',
    'author_email': 'jsmith@crackofdawn.onmicrosoft.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
