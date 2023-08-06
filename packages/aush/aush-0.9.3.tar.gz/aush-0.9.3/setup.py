# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['aush']
setup_kwargs = {
    'name': 'aush',
    'version': '0.9.3',
    'description': 'Pythonic subprocess library',
    'long_description': None,
    'author': 'Keith Devens',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kbd/aush',
    'py_modules': modules,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
