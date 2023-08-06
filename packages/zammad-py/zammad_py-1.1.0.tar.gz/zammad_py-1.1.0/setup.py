# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['zammad_py']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.25.1,<3.0.0']

setup_kwargs = {
    'name': 'zammad-py',
    'version': '1.1.0',
    'description': 'Python API client for zammad',
    'long_description': None,
    'author': 'Joe Paul',
    'author_email': 'joeirimpan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
