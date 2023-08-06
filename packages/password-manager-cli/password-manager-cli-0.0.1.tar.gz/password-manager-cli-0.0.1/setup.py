# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['src', 'src.menu', 'src.utils']

package_data = \
{'': ['*']}

install_requires = \
['rich>=12.5.1,<13.0.0']

entry_points = \
{'console_scripts': ['pwdm-cli = src.main:main']}

setup_kwargs = {
    'name': 'password-manager-cli',
    'version': '0.0.1',
    'description': 'Password Manager CLI',
    'long_description': None,
    'author': 'gbPagano',
    'author_email': 'guilhermebpagano@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
