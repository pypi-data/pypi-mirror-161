# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mobileiron_api', 'mobileiron_api.api', 'mobileiron_api.api.helpers']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.28.0,<3.0.0']

setup_kwargs = {
    'name': 'mobileiron-api',
    'version': '0.1.2',
    'description': '',
    'long_description': None,
    'author': 'n1ls',
    'author_email': 'lawiet47@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
