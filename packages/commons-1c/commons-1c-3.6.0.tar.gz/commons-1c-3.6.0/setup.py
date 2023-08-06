# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['commons_1c']

package_data = \
{'': ['*']}

install_requires = \
['appdirs', 'cjk-commons', 'loguru']

setup_kwargs = {
    'name': 'commons-1c',
    'version': '3.6.0',
    'description': 'Commons for 1C:Enterprise',
    'long_description': None,
    'author': 'Cujoko',
    'author_email': 'cujoko@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Cujoko/commons-1c',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
