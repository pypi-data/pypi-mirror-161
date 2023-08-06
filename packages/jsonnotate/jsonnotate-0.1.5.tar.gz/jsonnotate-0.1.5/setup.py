# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jsonnotate']

package_data = \
{'': ['*']}

install_requires = \
['typing-extensions>=4.2.0,<5.0.0']

setup_kwargs = {
    'name': 'jsonnotate',
    'version': '0.1.5',
    'description': '',
    'long_description': None,
    'author': 'Edward George',
    'author_email': 'edwardgeorge@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
