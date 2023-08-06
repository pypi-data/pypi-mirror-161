# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tainers']

package_data = \
{'': ['*']}

install_requires = \
['docker>=5.0.3,<6.0.0']

setup_kwargs = {
    'name': 'tainers',
    'version': '0.0.1',
    'description': 'Simple replacement for testcontainers-python',
    'long_description': None,
    'author': 'aperullo',
    'author_email': '18688190+aperullo@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
