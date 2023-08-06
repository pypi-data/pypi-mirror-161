# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['seamapi', 'seamapi.utils']

package_data = \
{'': ['*']}

install_requires = \
['dataclasses-json>=0.5.6,<0.6.0',
 'python-dotenv>=0.19.2,<0.20.0',
 'requests>=2.26.0,<3.0.0',
 'testcontainers[postgresql]>=3.4.2,<4.0.0']

setup_kwargs = {
    'name': 'seamapi',
    'version': '1.1.1',
    'description': "A Python Library for Seam's API https://getseam.com",
    'long_description': None,
    'author': 'Severin Ibarluzea',
    'author_email': 'seveibar@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
