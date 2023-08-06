# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['core']

package_data = \
{'': ['*']}

install_requires = \
['asyncio-mqtt>=0.12.1,<0.13.0', 'colorama>=0.4.4,<0.5.0']

setup_kwargs = {
    'name': 'policumbent-bob-core',
    'version': '0.3.1',
    'description': 'BOB common files',
    'long_description': None,
    'author': 'Gabriele Belluardo',
    'author_email': 'gabriele.belluardo@outlook.it',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
