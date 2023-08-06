# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ponodo', 'ponodo.abc', 'ponodo.console', 'ponodo.database', 'ponodo.routing']

package_data = \
{'': ['*']}

install_requires = \
['Werkzeug>=2.2.1,<3.0.0',
 'click>=8.1.3,<9.0.0',
 'inflect>=6.0.0,<7.0.0',
 'ipython>=8.4.0,<9.0.0']

setup_kwargs = {
    'name': 'ponodo',
    'version': '0.1.0a1',
    'description': 'Web Application Framework for Pythonista',
    'long_description': None,
    'author': 'Fathur Rohman',
    'author_email': 'hi.fathur.rohman@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
