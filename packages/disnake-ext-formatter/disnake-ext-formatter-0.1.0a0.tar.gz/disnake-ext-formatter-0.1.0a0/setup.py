# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['__init__']
install_requires = \
['disnake>=2.0,<3.0']

setup_kwargs = {
    'name': 'disnake-ext-formatter',
    'version': '0.1.0a0',
    'description': 'A simple string.Formatter for disnake types',
    'long_description': None,
    'author': 'onerandomusername',
    'author_email': 'genericusername414@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
