#!/usr/bin/env python

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'wridgets', 'version.py')) as f:
    exec(f.read())

with open(path.join(here, 'requirements.txt')) as f:
    requirements = f.read().split()

setup(
    name='wridgets',
    version=__version__,
    description='Wrapper around ipywidgets',
    author='Stelios Papadopoulos',
    author_email='stelios@spapa.us',
    packages=find_packages(exclude=[]),
    install_requires=requirements
)
