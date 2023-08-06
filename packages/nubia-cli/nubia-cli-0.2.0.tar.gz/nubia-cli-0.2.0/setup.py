# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nubia',
 'nubia.internal',
 'nubia.internal.commands',
 'nubia.internal.io',
 'nubia.internal.typing',
 'nubia.internal.ui']

package_data = \
{'': ['*']}

install_requires = \
['Pygments>=2.10.0,<3.0.0',
 'jellyfish>=0.8.9,<0.9.0',
 'prettytable>=2.4.0,<3.0.0',
 'prompt-toolkit>=3.0.23,<4.0.0',
 'pyparsing>=2.4.7,<3.0.0',
 'termcolor>=1.1.0,<2.0.0',
 'typing-inspect>=0.7.1,<0.8.0',
 'wcwidth>=0.2.5,<0.3.0']

setup_kwargs = {
    'name': 'nubia-cli',
    'version': '0.2.0',
    'description': "A fork of Meta's nubia, a framework for building beautiful shells.",
    'long_description': None,
    'author': 'Ahmed Soliman',
    'author_email': 'asoli@fb.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>3.7.2,<3.9',
}


setup(**setup_kwargs)
