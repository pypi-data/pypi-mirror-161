#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=line-too-long,missing-module-docstring,exec-used

import setuptools

with open('README.md', 'r') as file:
    long_description = file.read()

# DO NOT EDIT THIS NUMBER!
# IT IS AUTOMATICALLY CHANGED BY python-semantic-release
__version__ = "1.7.0"

setuptools.setup(
    name='gaussian_suite',
    version=__version__,
    author='Chilton Group',
    author_email='nicholas.chilton@manchester.ac.uk',
    description='A package for working with Gaussian input and output files',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://gitlab.com/chilton-group/gaussian_suite",
    project_urls={
        "Bug Tracker": "https://gitlab.com/chilton-group/gaussian_suite/-/issues",
        "Documentation": "https://chilton-group.gitlab.io/gaussian_suite"
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent'
        ],
    packages=setuptools.find_packages(),
    python_requires='>=3.9',
    install_requires=[
        'numpy',
        'scipy',
        'xyz_py>=5.0.0',
        'requests',
        'hpc_suite>=1.3.3',
        'deprecation'
        ],
    entry_points={
        'console_scripts': [
            'gaussian_suite = gaussian_suite.cli:main'
            ]
        }
    )
