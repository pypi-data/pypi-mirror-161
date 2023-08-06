# -*- coding: utf-8 -*-

import sys
from setuptools import setup, find_packages

if sys.version_info[0] < 3:
    with open("README.md", "r") as fh:
        long_description = fh.read()
else:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()

setup(
    name='pagarme-python',
    version='5.6.1',
    description='Pagarme API',
     
    long_description_content_type="text/markdown",
     author='Pagarme',
    author_email='support@pagar.me',
    url='https://github.com/pagarme/pagarme-core-api-python',
    packages=find_packages(),
    install_requires=[
        'requests>=2.9.1, <3.0',
        'jsonpickle>=0.7.1, <1.0',
        'cachecontrol>=0.11.7, <1.0',
        'python-dateutil>=2.5.3, <3.0'
    ]
)
