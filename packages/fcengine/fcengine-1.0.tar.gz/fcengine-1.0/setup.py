# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['fcengine']
setup_kwargs = {
    'name': 'fcengine',
    'version': '1.0',
    'description': 'Python module for making console games',
    'long_description': None,
    'author': 'Fab4key',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
