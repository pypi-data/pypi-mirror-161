# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['unipressed', 'unipressed.types']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.28.1,<3.0.0', 'typing-extensions>=4.3.0,<5.0.0']

setup_kwargs = {
    'name': 'unipressed',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Michael Milton',
    'author_email': 'michael.r.milton@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
