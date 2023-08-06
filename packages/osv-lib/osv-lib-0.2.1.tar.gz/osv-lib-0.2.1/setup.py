# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['osv']

package_data = \
{'': ['*']}

install_requires = \
['packageurl-python>=0.9.0,<0.10.0',
 'requests>=2.20.0,<3.0.0',
 'types-requests>=2.25.1,<3.0.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=3.4']}

setup_kwargs = {
    'name': 'osv-lib',
    'version': '0.2.1',
    'description': 'A library for querying OSV (https://osv.dev) distributed vulnerability database.',
    'long_description': None,
    'author': 'Paul Horton',
    'author_email': 'paul.horton@owasp.org',
    'maintainer': 'Paul Horton',
    'maintainer_email': 'paul.horton@owasp.org',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
