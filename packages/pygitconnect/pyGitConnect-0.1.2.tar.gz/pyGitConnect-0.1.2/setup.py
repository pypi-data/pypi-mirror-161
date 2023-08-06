# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['pygitconnect']
install_requires = \
['requests>=2.20.0,<3.0.0']

setup_kwargs = {
    'name': 'pygitconnect',
    'version': '0.1.2',
    'description': 'Simple API interface for more convenient work with GitHub service',
    'long_description': '# pyGitConnect\nPython module for more convenient work with GitHub.\n\n[![Downloads](https://pepy.tech/badge/pygitconnect)](https://pepy.tech/project/pygitconnect)\n[![Downloads](https://pepy.tech/badge/pygitconnect/month)](https://pepy.tech/project/pygitconnect)\n[![Downloads](https://pepy.tech/badge/pygitconnect/week)](https://pepy.tech/project/pygitconnect)\n[![Supported Versions](https://img.shields.io/pypi/pyversions/pygitconnect.svg)](https://pypi.org/project/pygitconnect)\n[![PyPI](https://img.shields.io/pypi/v/pygitconnect.svg)](https://pypi.org/project/pygitconnect/)\n[![PyPi](https://img.shields.io/pypi/format/pygitconnect)](https://pypi.org/project/pygitconnect/)\n![GitHub top language](https://img.shields.io/github/languages/top/tankalxat34/pygitconnect)\n[![GitHub last commit](https://img.shields.io/github/last-commit/tankalxat34/pygitconnect)](https://github.com/tankalxat34/pygitconnect/commits/main)        \n[![GitHub Release Date](https://img.shields.io/github/release-date/tankalxat34/pygitconnect)](https://github.com/tankalxat34/pygitconnect/releases)\n\n[![GitHub Repo stars](https://img.shields.io/github/stars/tankalxat34/pygitconnect?style=social)](https://github.com/tankalxat34/pygitconnect)\n\n# Example of use\n\n```py\nimport pyGitConnect\n\n# Creating User-object\nuserGitHub = pyGitConnect.User(\n    token="YOUR_TOKEN",\n    username="YOUR_USERNAME_ON_GITHUB",\n    email="YOUR_EMAIL_ON_GITHUB"\n)\n\n# conneting to file on GitHub\nfile = pyGitConnect.File(userGitHub, "repositoryName/branchName/path/to/your/file.txt")\n# getting readable text from file on GitHub\nprint(file.get().decode("UTF-8"))\n\n# reading file from your drive\nnewFile = pyGitConnect.NewFile(userGitHub, "B:\\\\GITHUB\\\\path\\\\to\\\\script.py")\n# pushing new file to your repository on GitHub\nprint(newFile.push("repositoryName/branchName/path/to/your/script/"))\n\n# connecting to uploaded file\nuploadedFile = pyGitConnect.File(userGitHub, "repositoryName/branchName/path/to/your/script/script.py")\n# printing readable content from uploaded file\nprint(uploadedFile.get().decode("UTF-8"))\n```',
    'author': 'tankalxat34',
    'author_email': 'tankalxat34@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tankalxat34/pyGitConnect',
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
