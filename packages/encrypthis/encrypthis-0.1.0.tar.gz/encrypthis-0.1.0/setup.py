# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['encrypthis']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0', 'cryptography>=37.0.4,<38.0.0']

entry_points = \
{'console_scripts': ['decrypt = encrypthis.cli:decrypt_cli',
                     'encrypt = encrypthis.cli:encrypt_cli',
                     'encrypthis = encrypthis.cli:main',
                     'genkey = encrypthis.util:genkey_cli']}

setup_kwargs = {
    'name': 'encrypthis',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': "'Gilad Barnea'",
    'author_email': 'giladbrn@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
