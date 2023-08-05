# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['pygitconnect']
setup_kwargs = {
    'name': 'pygitconnect',
    'version': '0.1.0',
    'description': 'Simple API interface for more convenient work with GitHub service',
    'long_description': None,
    'author': 'tankalxat34',
    'author_email': 'tankalxat34@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
