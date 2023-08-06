# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['qottoauth']

package_data = \
{'': ['*']}

install_requires = \
['PyJWT>=2.4.0,<3.0.0',
 'cryptography>=37.0.0',
 'eventy>=3.1.0',
 'gql[requests]>=3.0.0',
 'requests>=2.0.0']

setup_kwargs = {
    'name': 'qotto-auth-client',
    'version': '0.1.0',
    'description': 'Qotto/QottoAuthClient',
    'long_description': '# Qotto Auth Client\n\nThe python package `qotto-auth-client` is a client for the API `qotto-auth` which will soon be open sourced.\n\nIt allows to manage a scoped permission and authentication system.\n\nMore information coming soon...\n\n',
    'author': 'Qotto Dev Team',
    'author_email': 'dev@qotto.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
