# This file is a part of the AnyBlok / Sale project
#
#    Copyright (C) 2018 Franck Bret <franckbret@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
# -*- coding: utf-8 -*-
"""Setup script for anyblok_sale"""

from setuptools import setup, find_packages
import os


here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst'),
          'r', encoding='utf-8') as readme_file:
    readme = readme_file.read()

with open(os.path.join(here, 'CHANGELOG.rst'),
          'r', encoding='utf-8') as changelog_file:
    changelog = changelog_file.read()

with open(os.path.join(here, 'VERSION'),
          'r', encoding='utf-8') as version_file:
    version = version_file.read().strip()

requirements = [
    'anyblok',
    'anyblok_mixins',
    'anyblok_marshmallow',
    'anyblok_attachment',
    'anyblok_address',
    'anyblok_product',
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='anyblok_sale',
    version=version,
    description="Sale management",
    long_description=readme + '\n\n' + changelog,
    author="Franck Bret",
    author_email='f.bret@sensee.com',
    url='https://github.com/AnyBlok/anyblok_sale',
    packages=find_packages(),
    entry_points={
        'bloks': [
            'sale=anyblok_sale.bloks.sale:SaleBlok',
        ],
    },
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords='anyblok_sale, anyblok, sale',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
)
