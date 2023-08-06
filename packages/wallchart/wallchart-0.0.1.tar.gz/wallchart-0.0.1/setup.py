# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wallchart']

package_data = \
{'': ['*'], 'wallchart': ['static/*', 'templates/*', 'templates/includes/*']}

install_requires = \
['Flask>=2.0.1,<3.0.0',
 'PyYAML>=5.4.1,<6.0.0',
 'bcrypt>=3.2.0,<4.0.0',
 'peewee>=3.14.4,<4.0.0',
 'phonenumbers>=8.12.31,<9.0.0',
 'python-slugify>=5.0.2,<6.0.0']

setup_kwargs = {
    'name': 'wallchart',
    'version': '0.0.1',
    'description': '',
    'long_description': None,
    'author': 'Paul Spooren',
    'author_email': 'mail@aparcar.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
