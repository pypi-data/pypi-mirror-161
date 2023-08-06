# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['src', 'src.data', 'src.menu', 'src.utils']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=1.4.39,<2.0.0',
 'argon2-cffi>=21.3.0,<22.0.0',
 'click>=8.1.3,<9.0.0',
 'cryptography>=37.0.4,<38.0.0',
 'python-dotenv>=0.20.0,<0.21.0',
 'rich>=12.5.1,<13.0.0']

entry_points = \
{'console_scripts': ['mankey = src.main:main']}

setup_kwargs = {
    'name': 'password-manager-cli',
    'version': '0.1.3',
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
