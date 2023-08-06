#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
iris-validator
Simple class + functions for validating StationXML
against IRIS Validation Rules

:copyright:
    Mike Hagerty (m.hagerty@isti.com), 2020-2022
:license:
    GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html)
"""

from codecs import open
import os
from os import path
from setuptools import setup, find_packages

#import versioneer
import iris_validator

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as readme_file:
    readme = readme_file.read()

with open(path.join(here, 'HISTORY.rst'), encoding='utf-8') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    'obspy>=1.2',
]

test_requirements = [
    # TODO: put package test requirements here
    'tox',
    'pytest',
    'pytest-runner',
]

import sys
import site
#print("***** MTH: sys.prefix=[%s] site.USER_BASE=[%s]" % (sys.prefix, site.USER_BASE))
py_version = '%s.%s' % (sys.version_info[0], sys.version_info[1])
path = 'lib/python%s/site-packages/iris_validator' % py_version
#data_dir = os.path.join(path, 'fdsn-schema')
#data_files = [(data_dir, ["yasmine_cli/fdsn-schema/fdsn-station-1.0.xsd",
                          #"yasmine_cli/fdsn-schema/fdsn-station-1.1.xsd"]
             #)]

setup(
    name='iris-validator',
    #version=versioneer.get_version(),
    #cmdclass=versioneer.get_cmdclass(),
    version=iris_validator.__version__,
    description="Implementation of IRIS StationXML validation rules",
    #long_description=readme + '\n\n' + history,
    long_description=readme,
    long_description_content_type='text/markdown',
    author="Mike Hagerty",
    author_email='mhagerty@isti.com',
    url='https://gitlab.isti.com/mhagerty/iris-validator',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    #data_files = data_files,
    entry_points={
        'console_scripts':[
            'iris-validator=iris_validator.cmdline:main',
            ],
        },
    include_package_data=True,
    package_data = { 'iris_validator': ['iris_resources/*',] },
    install_requires=requirements,
    license="MIT",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
)
