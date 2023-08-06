#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=line-too-long,missing-module-docstring,exec-used

import setuptools

with open('README.md', 'r') as file:
    long_description = file.read()

# DO NOT EDIT THIS NUMBER!
# IT IS AUTOMATICALLY CHANGED BY python-semantic-release
__version__ = "1.4.0"

setuptools.setup(
    name='hpc-suite',
    version=__version__,
    author='Chilton Group',
    author_email='nicholas.chilton@manchester.ac.uk',
    description='A package for working with data on HPC platforms',
    url="https://gitlab.com/chilton-group/hpc_suite",
    project_urls={
        "Bug Tracker": "https://gitlab.com/chilton-group/hpc_suite/-/issues",
        "Documentation": "https://chilton-group.gitlab.io/hpc_suite"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    install_requires=['numpy', 'h5py'],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'hpc_suite = hpc_suite.cli:main',
            ],
        }
)
